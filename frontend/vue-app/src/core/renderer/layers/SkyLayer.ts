import * as THREE from 'three';
import type { StarMeta } from '../../../types/star-meta';
import { AstroCoordinates } from '../../astronomy/Coordinates';

/**
 * Sky Layer（天穹层）
 * 渲染星空、银河、星座 - 永远在"无限远"
 */
export class SkyLayer {
    private scene: THREE.Scene;
    private skyGroup: THREE.Group;
    
    // 星点系统
    private starPoints: THREE.Points | null = null;
    private starMaterial: THREE.ShaderMaterial | null = null;
    
    // 银河层
    private milkyWay: THREE.Mesh | null = null;
    
    // 天球半径（极大，模拟无限远）
    private readonly SKY_RADIUS = 10000;
    
    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.skyGroup = new THREE.Group();
        this.skyGroup.name = 'SkyLayer';
        this.scene.add(this.skyGroup);
    }
    
    /**
     * 加载真实星表
     */
    public async loadStarField(stars: StarMeta[]): Promise<void> {
        console.log('🌟 Sky Layer: 加载真实星表');
        
        // 过滤可见恒星（肉眼极限 ~6.5 等）
        const visibleStars = stars.filter(s => s.magnitude <= 6.5);
        
        const geometry = new THREE.BufferGeometry();
        const positions: number[] = [];
        const magnitudes: number[] = [];
        const colors: number[] = [];
        
        visibleStars.forEach(star => {
            // 转换为天球坐标
            const pos = AstroCoordinates.raDecToVector3(
                star.equatorialCoordinate.rightAscension,
                star.equatorialCoordinate.declination,
                this.SKY_RADIUS
            );
            positions.push(pos.x, pos.y, pos.z);
            magnitudes.push(star.magnitude);
            
            // B-V 色温转 RGB
            const color = this.bvToRGB(star.bvColor);
            colors.push(color.r, color.g, color.b);
        });
        
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('aMagnitude', new THREE.Float32BufferAttribute(magnitudes, 1));
        geometry.setAttribute('aColor', new THREE.Float32BufferAttribute(colors, 3));
        
        this.starMaterial = this.createStarShader();
        this.starPoints = new THREE.Points(geometry, this.starMaterial);
        this.starPoints.frustumCulled = false; // 天球永远可见
        this.skyGroup.add(this.starPoints);
        
        console.log(`✨ 渲染 ${visibleStars.length} 颗真实恒星`);
    }
    
    /**
     * 创建专业星点 Shader
     */
    private createStarShader(): THREE.ShaderMaterial {
        return new THREE.ShaderMaterial({
            uniforms: {
                uTime: { value: 0 },
                uExposure: { value: 1.0 },      // 曝光控制
                uPixelRatio: { value: window.devicePixelRatio }
            },
            vertexShader: `
                attribute float aMagnitude;
                attribute vec3 aColor;
                
                uniform float uExposure;
                uniform float uPixelRatio;
                
                varying vec3 vColor;
                varying float vIntensity;
                
                void main() {
                    vColor = aColor;
                    
                    // 星等转亮度：I = 10^(-0.4 * mag)
                    float intensity = pow(10.0, -0.4 * aMagnitude);
                    vIntensity = intensity * uExposure;
                    
                    // 计算星点大小（基于亮度，带曝光补偿）
                    float baseSize = sqrt(intensity) * 30.0;
                    float size = baseSize * uPixelRatio;
                    
                    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                    gl_Position = projectionMatrix * mvPosition;
                    
                    // 大小不随距离变化（天球无限远）
                    gl_PointSize = size;
                }
            `,
            fragmentShader: `
                varying vec3 vColor;
                varying float vIntensity;
                
                void main() {
                    // 柔和核心 + 微弱光晕
                    vec2 coord = gl_PointCoord - vec2(0.5);
                    float dist = length(coord);
                    
                    // 核心（50% 半径内）
                    float core = 1.0 - smoothstep(0.0, 0.3, dist);
                    
                    // 外层光晕（30%-50% 半径）
                    float halo = (1.0 - smoothstep(0.3, 0.5, dist)) * 0.3;
                    
                    float alpha = (core + halo) * vIntensity;
                    
                    if (alpha < 0.01) discard;
                    
                    // HDR 颜色（亮星可以超过 1.0）
                    vec3 hdrColor = vColor * vIntensity;
                    
                    gl_FragColor = vec4(hdrColor, alpha);
                }
            `,
            transparent: true,
            depthWrite: false,
            depthTest: true,
            blending: THREE.AdditiveBlending
        });
    }
    
    /**
     * B-V 色指数转 RGB（物理准确）
     */
    private bvToRGB(bv: number): THREE.Color {
        // 基于黑体辐射和天文测光的映射
        let r: number, g: number, b: number;
        
        if (bv < -0.4) {
            // 极蓝星（O型）
            r = 0.6; g = 0.7; b = 1.0;
        } else if (bv < 0) {
            // 蓝星（B型）
            const t = (bv + 0.4) / 0.4;
            r = 0.6 + t * 0.2;
            g = 0.7 + t * 0.2;
            b = 1.0;
        } else if (bv < 0.5) {
            // 蓝白-白星（A, F型）
            const t = bv / 0.5;
            r = 0.8 + t * 0.2;
            g = 0.9 + t * 0.1;
            b = 1.0 - t * 0.1;
        } else if (bv < 1.0) {
            // 白-黄星（G型，类太阳）
            const t = (bv - 0.5) / 0.5;
            r = 1.0;
            g = 1.0 - t * 0.15;
            b = 0.9 - t * 0.25;
        } else if (bv < 1.5) {
            // 橙星（K型）
            const t = (bv - 1.0) / 0.5;
            r = 1.0;
            g = 0.85 - t * 0.2;
            b = 0.65 - t * 0.25;
        } else {
            // 红星（M型）
            const t = Math.min(1, (bv - 1.5) / 0.5);
            r = 1.0;
            g = 0.65 - t * 0.25;
            b = 0.4 - t * 0.2;
        }
        
        return new THREE.Color(r, g, b);
    }
    
    /**
     * 创建银河层（HDR 天球或程序化）
     */
    public createMilkyWay(): void {
        const geometry = new THREE.SphereGeometry(this.SKY_RADIUS * 0.99, 64, 64);
        
        // 程序化银河 Shader
        const material = new THREE.ShaderMaterial({
            uniforms: {
                uTime: { value: 0 }
            },
            vertexShader: `
                varying vec3 vPosition;
                varying vec2 vUv;
                
                void main() {
                    vPosition = position;
                    vUv = uv;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                varying vec3 vPosition;
                varying vec2 vUv;
                uniform float uTime;
                
                // 简化的银河噪声
                float noise(vec3 p) {
                    return fract(sin(dot(p, vec3(12.9898, 78.233, 45.5432))) * 43758.5453);
                }
                
                void main() {
                    // 银河带（赤道平面附近）
                    float galacticBand = abs(vPosition.y / length(vPosition));
                    float bandMask = 1.0 - smoothstep(0.0, 0.3, galacticBand);
                    
                    // 噪声纹理
                    float n = noise(vPosition * 0.1);
                    float turbulence = noise(vPosition * 0.5) * 0.5;
                    
                    // 银河颜色（淡紫蓝白）
                    vec3 milkyColor = mix(
                        vec3(0.1, 0.05, 0.15),  // 深蓝紫
                        vec3(0.3, 0.25, 0.35),  // 淡紫白
                        n
                    );
                    
                    float alpha = bandMask * (n * 0.3 + turbulence * 0.2);
                    
                    gl_FragColor = vec4(milkyColor, alpha);
                }
            `,
            transparent: true,
            side: THREE.BackSide,
            depthWrite: false
        });
        
        this.milkyWay = new THREE.Mesh(geometry, material);
        this.milkyWay.frustumCulled = false;
        this.skyGroup.add(this.milkyWay);
        
        console.log('🌌 银河层已创建');
    }
    
    /**
     * 更新（跟随相机位置，不跟随旋转）
     */
    public update(cameraPosition: THREE.Vector3, deltaTime: number): void {
        // 天穹层永远跟随相机位置（保持在无限远）
        this.skyGroup.position.copy(cameraPosition);
        
        // 更新星点闪烁（非常微弱）
        if (this.starMaterial) {
            this.starMaterial.uniforms.uTime.value += deltaTime;
        }
        
        // 银河缓慢流动（可选）
        if (this.milkyWay && this.milkyWay.material instanceof THREE.ShaderMaterial) {
            this.milkyWay.material.uniforms.uTime.value += deltaTime * 0.01;
        }
    }
    
    /**
     * 设置曝光（进入太阳/亮星附近时降低）
     */
    public setExposure(exposure: number): void {
        if (this.starMaterial) {
            this.starMaterial.uniforms.uExposure.value = exposure;
        }
    }
    
    /**
     * 清理
     */
    public dispose(): void {
        if (this.starPoints) {
            this.starPoints.geometry.dispose();
            if (this.starMaterial) this.starMaterial.dispose();
        }
        if (this.milkyWay) {
            this.milkyWay.geometry.dispose();
            if (this.milkyWay.material instanceof THREE.Material) {
                this.milkyWay.material.dispose();
            }
        }
        this.scene.remove(this.skyGroup);
    }
}
