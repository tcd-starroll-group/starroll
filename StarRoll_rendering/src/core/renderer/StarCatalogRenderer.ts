import * as THREE from 'three';
import type { StarMeta, ConstellationLines } from '../../types/star-meta';
import { AstroCoordinates } from '../astronomy/Coordinates';
import { createStarPointMaterial } from '../materials/Shaders';
import { ConstellationLineMaterial } from '../materials/ConstellationMaterials';

/**
 * 真实星表渲染器
 * 使用真实的恒星数据渲染星空，支持颜色、亮度和星座连线
 */
export class StarCatalogRenderer {
    private scene: THREE.Scene;
    private starPoints: THREE.Points | null = null;
    private starsMaterial: THREE.ShaderMaterial | null = null;
    private constellationLines: THREE.Group = new THREE.Group();
    private starMap: Map<number, StarMeta> = new Map(); // HIP -> StarMeta
    
    // 配置参数
    private readonly STAR_SPHERE_RADIUS = 500;  // 天球半径
    private readonly MIN_MAGNITUDE = 8.0;        // 最暗星等限制
    private readonly SIZE_SCALE = 1.0;           // 星星大小缩放因子
    
    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.scene.add(this.constellationLines);
    }
    
    /**
     * 加载并渲染星表数据
     * @param stars 星表数据数组
     * @param constellations 星座连线定义（可选）
     */
    public async loadStarCatalog(
        stars: StarMeta[], 
        constellations?: ConstellationLines[]
    ): Promise<void> {
        console.log(`Loading ${stars.length} stars...`);
        
        // 1. 构建星星索引
        stars.forEach(star => {
            this.starMap.set(star.hIP, star);
        });
        
        // 2. 过滤和创建星点
        this.createStarPoints(stars);
        
        // 3. 创建星座连线
        if (constellations && constellations.length > 0) {
            this.createConstellationLines(constellations);
        }
        
        console.log('Star catalog loaded successfully!');
    }
    
    /**
     * 创建星点渲染
     */
    private createStarPoints(stars: StarMeta[]): void {
        // 过滤掉太暗的星星
        const visibleStars = stars.filter(star => star.magnitude <= this.MIN_MAGNITUDE);
        
        console.log(`Rendering ${visibleStars.length} visible stars (mag <= ${this.MIN_MAGNITUDE})`);
        
        const geometry = new THREE.BufferGeometry();
        const positions: number[] = [];
        const sizes: number[] = [];
        const colors: number[] = [];
        
        visibleStars.forEach(star => {
            // 坐标转换
            const pos = AstroCoordinates.raDecToVector3(
                star.equatorialCoordinate.rightAscension,
                star.equatorialCoordinate.declination,
                this.STAR_SPHERE_RADIUS
            );
            positions.push(pos.x, pos.y, pos.z);
            
            // 星等转换为大小 (星等越小越亮)
            // 使用对数刻度模拟真实亮度差异
            const apparentSize = Math.pow(2.512, (this.MIN_MAGNITUDE - star.magnitude)) * this.SIZE_SCALE;
            const size = Math.max(0.5, Math.min(apparentSize, 10)); // 限制大小范围
            sizes.push(size);
            
            // B-V 色指数转换为 RGB 颜色
            const color = this.bvColorToRGB(star.bvColor);
            colors.push(color.r, color.g, color.b);
        });
        
        // 设置几何体属性
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('aScale', new THREE.Float32BufferAttribute(sizes, 1));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        
        // 创建材质
        this.starsMaterial = this.createStarMaterial();
        
        // 创建星点系统
        this.starPoints = new THREE.Points(geometry, this.starsMaterial);
        this.scene.add(this.starPoints);
    }
    
    /**
     * 创建支持顶点颜色的星点材质
     */
    private createStarMaterial(): THREE.ShaderMaterial {
        return new THREE.ShaderMaterial({
            uniforms: {
                uTime: { value: 0 },
                uSize: { value: 4.0 },
                uColor: { value: new THREE.Color(0xffffff) }
            },
            vertexShader: `
                attribute float aScale;
                attribute vec3 color;
                
                uniform float uSize;
                uniform float uTime;
                
                varying vec3 vColor;
                varying float vAlpha;
                
                void main() {
                    vColor = color;
                    
                    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                    
                    // 闪烁效果 (基于位置的相位偏移)
                    float phase = dot(position, vec3(0.1, 0.2, 0.3));
                    float twinkle = 0.8 + 0.2 * sin(uTime * 2.0 + phase * 10.0);
                    vAlpha = twinkle;
                    
                    // 根据星等调整大小，距离衰减较小
                    gl_PointSize = aScale * uSize * (300.0 / -mvPosition.z);
                    gl_Position = projectionMatrix * mvPosition;
                }
            `,
            fragmentShader: `
                varying vec3 vColor;
                varying float vAlpha;
                
                void main() {
                    // 圆形星点
                    vec2 coord = gl_PointCoord - vec2(0.5);
                    float dist = length(coord);
                    if (dist > 0.5) discard;
                    
                    // 柔和的边缘
                    float alpha = 1.0 - smoothstep(0.3, 0.5, dist);
                    alpha *= vAlpha;
                    
                    // 应用星星颜色
                    gl_FragColor = vec4(vColor, alpha);
                }
            `,
            transparent: true,
            depthWrite: false,
            blending: THREE.AdditiveBlending
        });
    }
    
    /**
     * B-V 色指数转换为 RGB 颜色
     * B-V < 0: 蓝色 (热星)
     * B-V = 0.5: 白色 (类太阳)
     * B-V > 1.5: 红色 (冷星)
     */
    private bvColorToRGB(bv: number): THREE.Color {
        // 简化的颜色映射
        let r: number, g: number, b: number;
        
        if (bv < 0) {
            // 蓝色星 (O, B 型)
            const t = Math.max(0, (bv + 0.4) / 0.4);
            r = 0.7 + t * 0.3;
            g = 0.8 + t * 0.2;
            b = 1.0;
        } else if (bv < 0.5) {
            // 蓝白色 (A, F 型)
            const t = bv / 0.5;
            r = 0.8 + t * 0.2;
            g = 0.9 + t * 0.1;
            b = 1.0 - t * 0.1;
        } else if (bv < 1.0) {
            // 白色到黄色 (G 型，类太阳)
            const t = (bv - 0.5) / 0.5;
            r = 1.0;
            g = 1.0 - t * 0.2;
            b = 0.9 - t * 0.3;
        } else if (bv < 1.5) {
            // 橙色 (K 型)
            const t = (bv - 1.0) / 0.5;
            r = 1.0;
            g = 0.8 - t * 0.2;
            b = 0.6 - t * 0.3;
        } else {
            // 红色 (M 型)
            const t = Math.min(1, (bv - 1.5) / 0.5);
            r = 1.0;
            g = 0.6 - t * 0.3;
            b = 0.3 - t * 0.2;
        }
        
        return new THREE.Color(r, g, b);
    }
    
    /**
     * 创建星座连线
     */
    private createConstellationLines(constellations: ConstellationLines[]): void {
        console.log(`Creating ${constellations.length} constellation lines...`);
        
        constellations.forEach(constellation => {
            const group = new THREE.Group();
            group.name = constellation.id;
            
            const positions: number[] = [];
            let validLines = 0;
            
            constellation.lines.forEach(([hip1, hip2]) => {
                const star1 = this.starMap.get(hip1);
                const star2 = this.starMap.get(hip2);
                
                if (star1 && star2) {
                    const pos1 = AstroCoordinates.raDecToVector3(
                        star1.equatorialCoordinate.rightAscension,
                        star1.equatorialCoordinate.declination,
                        this.STAR_SPHERE_RADIUS
                    );
                    const pos2 = AstroCoordinates.raDecToVector3(
                        star2.equatorialCoordinate.rightAscension,
                        star2.equatorialCoordinate.declination,
                        this.STAR_SPHERE_RADIUS
                    );
                    
                    positions.push(pos1.x, pos1.y, pos1.z);
                    positions.push(pos2.x, pos2.y, pos2.z);
                    validLines++;
                } else {
                    console.warn(`Stars not found for constellation ${constellation.id}: HIP ${hip1} or ${hip2}`);
                }
            });
            
            if (positions.length > 0) {
                const geometry = new THREE.BufferGeometry();
                geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
                
                const lines = new THREE.LineSegments(geometry, ConstellationLineMaterial);
                group.add(lines);
                
                console.log(`Constellation ${constellation.name} (${constellation.id}): ${validLines} lines`);
            }
            
            this.constellationLines.add(group);
        });
    }
    
    /**
     * 更新动画
     */
    public update(deltaTime: number): void {
        if (this.starsMaterial) {
            this.starsMaterial.uniforms.uTime.value += deltaTime;
        }
    }
    
    /**
     * 设置星座连线可见性
     */
    public setConstellationLinesVisible(visible: boolean): void {
        this.constellationLines.visible = visible;
    }
    
    /**
     * 设置单个星座可见性
     */
    public setConstellationVisible(id: string, visible: boolean): void {
        const group = this.constellationLines.children.find(g => g.name === id);
        if (group) {
            group.visible = visible;
        }
    }
    
    /**
     * 获取星表统计信息
     */
    public getStats(): { totalStars: number, visibleStars: number, constellations: number } {
        const visibleStars = this.starPoints?.geometry.attributes.position.count || 0;
        return {
            totalStars: this.starMap.size,
            visibleStars: visibleStars,
            constellations: this.constellationLines.children.length
        };
    }
    
    /**
     * 清理资源
     */
    public dispose(): void {
        if (this.starPoints) {
            this.starPoints.geometry.dispose();
            if (this.starsMaterial) {
                this.starsMaterial.dispose();
            }
            this.scene.remove(this.starPoints);
        }
        
        this.constellationLines.children.forEach(group => {
            group.children.forEach(child => {
                if (child instanceof THREE.LineSegments) {
                    child.geometry.dispose();
                }
            });
        });
        this.scene.remove(this.constellationLines);
    }
}
