import * as THREE from 'three';
import type { StarMeta, ConstellationLines } from '../../types/star-meta';
import type { ConstellationModel } from '../data/constellation-models';
import { AstroCoordinates } from '../astronomy/Coordinates';
import { createStarPointMaterial } from '../materials/Shaders';
import { ConstellationLineMaterial, GlassConstellationMaterial } from '../materials/ConstellationMaterials';
import { ModelLoader } from '../utils/GLTFLoader';

/**
 * 增强版星表渲染器
 * 支持加载星座 3D 模型并与星表数据结合
 */
export class StarCatalogRendererWithModels {
    private scene: THREE.Scene;
    private starPoints: THREE.Points | null = null;
    private starsMaterial: THREE.ShaderMaterial | null = null;
    private constellationLines: THREE.Group = new THREE.Group();
    private constellationModels: THREE.Group = new THREE.Group();
    private starMap: Map<number, StarMeta> = new Map();
    
    // 配置参数
    private readonly STAR_SPHERE_RADIUS = 500;
    private readonly MIN_MAGNITUDE = 6.5;
    private readonly SIZE_SCALE = 2.0;
    private readonly MODEL_DISTANCE = 480; // 模型距离，比星星略近
    
    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.constellationLines.name = 'ConstellationLines';
        this.constellationModels.name = 'ConstellationModels';
        this.scene.add(this.constellationLines);
        this.scene.add(this.constellationModels);
    }
    
    /**
     * 加载星表、星座连线和 3D 模型
     */
    public async loadStarCatalog(
        stars: StarMeta[], 
        constellations?: ConstellationLines[],
        models?: ConstellationModel[]
    ): Promise<void> {
        console.log(`🌟 加载星表：${stars.length} 颗恒星`);
        
        // 1. 构建星星索引
        stars.forEach(star => {
            this.starMap.set(star.hIP, star);
        });
        
        // 2. 创建星点
        this.createStarPoints(stars);
        
        // 3. 创建星座连线
        if (constellations && constellations.length > 0) {
            this.createConstellationLines(constellations);
        }
        
        // 4. 加载星座 3D 模型
        if (models && models.length > 0) {
            await this.loadConstellationModels(models);
        }
        
        console.log('✅ 星表渲染系统加载完成');
    }
    
    /**
     * 创建星点渲染
     */
    private createStarPoints(stars: StarMeta[]): void {
        const visibleStars = stars.filter(star => star.magnitude <= this.MIN_MAGNITUDE);
        
        console.log(`✨ 渲染 ${visibleStars.length} 颗可见恒星 (mag ≤ ${this.MIN_MAGNITUDE})`);
        
        const geometry = new THREE.BufferGeometry();
        const positions: number[] = [];
        const sizes: number[] = [];
        const colors: number[] = [];
        
        visibleStars.forEach(star => {
            const pos = AstroCoordinates.raDecToVector3(
                star.equatorialCoordinate.rightAscension,
                star.equatorialCoordinate.declination,
                this.STAR_SPHERE_RADIUS
            );
            positions.push(pos.x, pos.y, pos.z);
            
            const apparentSize = Math.pow(2.512, (this.MIN_MAGNITUDE - star.magnitude)) * this.SIZE_SCALE;
            const size = Math.max(0.5, Math.min(apparentSize, 10));
            sizes.push(size);
            
            const color = this.bvColorToRGB(star.bvColor);
            colors.push(color.r, color.g, color.b);
        });
        
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('aScale', new THREE.Float32BufferAttribute(sizes, 1));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        
        this.starsMaterial = this.createStarMaterial();
        this.starPoints = new THREE.Points(geometry, this.starsMaterial);
        this.starPoints.name = 'Stars';
        this.scene.add(this.starPoints);
    }
    
    /**
     * 创建星点材质
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
                    
                    float phase = dot(position, vec3(0.1, 0.2, 0.3));
                    float twinkle = 0.8 + 0.2 * sin(uTime * 2.0 + phase * 10.0);
                    vAlpha = twinkle;
                    
                    gl_PointSize = aScale * uSize * (300.0 / -mvPosition.z);
                    gl_Position = projectionMatrix * mvPosition;
                }
            `,
            fragmentShader: `
                varying vec3 vColor;
                varying float vAlpha;
                
                void main() {
                    vec2 coord = gl_PointCoord - vec2(0.5);
                    float dist = length(coord);
                    if (dist > 0.5) discard;
                    
                    float alpha = 1.0 - smoothstep(0.3, 0.5, dist);
                    alpha *= vAlpha;
                    
                    gl_FragColor = vec4(vColor, alpha);
                }
            `,
            transparent: true,
            depthWrite: false,
            blending: THREE.AdditiveBlending
        });
    }
    
    /**
     * B-V 色指数转 RGB
     */
    private bvColorToRGB(bv: number): THREE.Color {
        let r: number, g: number, b: number;
        
        if (bv < 0) {
            const t = Math.max(0, (bv + 0.4) / 0.4);
            r = 0.7 + t * 0.3;
            g = 0.8 + t * 0.2;
            b = 1.0;
        } else if (bv < 0.5) {
            const t = bv / 0.5;
            r = 0.8 + t * 0.2;
            g = 0.9 + t * 0.1;
            b = 1.0 - t * 0.1;
        } else if (bv < 1.0) {
            const t = (bv - 0.5) / 0.5;
            r = 1.0;
            g = 1.0 - t * 0.2;
            b = 0.9 - t * 0.3;
        } else if (bv < 1.5) {
            const t = (bv - 1.0) / 0.5;
            r = 1.0;
            g = 0.8 - t * 0.2;
            b = 0.6 - t * 0.3;
        } else {
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
        console.log(`🔗 创建 ${constellations.length} 个星座连线`);
        
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
                }
            });
            
            if (positions.length > 0) {
                const geometry = new THREE.BufferGeometry();
                geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
                
                const lines = new THREE.LineSegments(geometry, ConstellationLineMaterial);
                group.add(lines);
                
                console.log(`  ${constellation.name}: ${validLines} 条连线`);
            }
            
            this.constellationLines.add(group);
        });
    }
    
    /**
     * 加载星座 3D 模型
     */
    private async loadConstellationModels(models: ConstellationModel[]): Promise<void> {
        console.log(`🎨 加载 ${models.length} 个星座 3D 模型...`);
        
        const loadPromises = models.map(async (modelConfig) => {
            try {
                // 加载模型
                const model = await ModelLoader.loadModel(modelConfig.modelPath);
                
                // 计算模型位置
                let position: THREE.Vector3;
                
                if (modelConfig.centerHIP) {
                    // 使用中心恒星位置
                    const centerStar = this.starMap.get(modelConfig.centerHIP);
                    if (centerStar) {
                        position = AstroCoordinates.raDecToVector3(
                            centerStar.equatorialCoordinate.rightAscension,
                            centerStar.equatorialCoordinate.declination,
                            this.MODEL_DISTANCE
                        );
                    } else {
                        console.warn(`⚠️ 未找到中心恒星 HIP ${modelConfig.centerHIP}，跳过模型 ${modelConfig.name}`);
                        return;
                    }
                } else {
                    // 默认位置（如果没有指定中心恒星）
                    position = new THREE.Vector3(0, 0, this.MODEL_DISTANCE);
                }
                
                // 设置模型
                model.position.copy(position);
                model.lookAt(0, 0, 0);
                
                // 应用缩放
                const scale = modelConfig.scale || 50;
                model.scale.setScalar(scale);
                
                // 应用玻璃材质到模型
                this.applyGlassMaterialToModel(model);
                
                // 添加到场景
                model.name = modelConfig.id;
                model.userData = { 
                    constellationId: modelConfig.id,
                    constellationName: modelConfig.name,
                    centerPosition: position.clone()
                };
                
                this.constellationModels.add(model);
                
                console.log(`  ✅ ${modelConfig.name} 模型加载成功`);
                
            } catch (error) {
                console.error(`  ❌ ${modelConfig.name} 模型加载失败:`, error);
            }
        });
        
        await Promise.all(loadPromises);
        console.log(`🎉 星座模型加载完成！`);
    }
    
    /**
     * 应用玻璃材质到模型的所有网格
     */
    private applyGlassMaterialToModel(model: THREE.Group): void {
        model.traverse((child: any) => {
            if (child.isMesh) {
                // 为每个网格创建独立的玻璃材质实例
                const glassMaterial = GlassConstellationMaterial.clone();
                
                // 可以根据需要调整颜色
                // 例如：不同星座使用不同颜色
                // glassMaterial.uniforms.uColor.value.setHex(0x88ccff);
                
                child.material = glassMaterial;
                child.material.needsUpdate = true;
                
                // 确保投射和接收阴影（虽然玻璃材质可能不太需要）
                child.castShadow = true;
                child.receiveShadow = true;
            }
        });
    }
    
    /**
     * 更新动画
     */
    public update(deltaTime: number): void {
        // 更新星点闪烁
        if (this.starsMaterial) {
            this.starsMaterial.uniforms.uTime.value += deltaTime;
        }
        
        // 模型自转和材质动画
        this.constellationModels.children.forEach((model) => {
            model.rotation.y += deltaTime * 0.1;
            
            // 更新玻璃材质的呼吸效果
            model.traverse((child: any) => {
                if (child.isMesh && child.material && child.material.uniforms && child.material.uniforms.uTime) {
                    child.material.uniforms.uTime.value += deltaTime;
                }
            });
        });
    }
    
    /**
     * 设置星座连线可见性
     */
    public setConstellationLinesVisible(visible: boolean): void {
        this.constellationLines.visible = visible;
    }
    
    /**
     * 设置星座模型可见性
     */
    public setConstellationModelsVisible(visible: boolean): void {
        this.constellationModels.visible = visible;
    }
    
    /**
     * 设置单个星座可见性
     */
    public setConstellationVisible(id: string, visible: boolean): void {
        const lineGroup = this.constellationLines.children.find(g => g.name === id);
        if (lineGroup) {
            lineGroup.visible = visible;
        }
        
        const model = this.constellationModels.children.find(m => m.name === id);
        if (model) {
            model.visible = visible;
        }
    }
    
    /**
     * 获取统计信息
     */
    public getStats(): { 
        totalStars: number, 
        visibleStars: number, 
        constellations: number,
        models: number 
    } {
        const visibleStars = this.starPoints?.geometry.attributes.position.count || 0;
        return {
            totalStars: this.starMap.size,
            visibleStars: visibleStars,
            constellations: this.constellationLines.children.length,
            models: this.constellationModels.children.length
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
        
        this.constellationModels.children.forEach(model => {
            model.traverse((child: any) => {
                if (child.geometry) child.geometry.dispose();
                if (child.material) {
                    if (Array.isArray(child.material)) {
                        child.material.forEach((m: any) => m.dispose());
                    } else {
                        child.material.dispose();
                    }
                }
            });
        });
        
        this.scene.remove(this.constellationLines);
        this.scene.remove(this.constellationModels);
    }
}
