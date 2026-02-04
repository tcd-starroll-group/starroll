import * as THREE from 'three';
import type { StarMeta } from '../../types/star-meta';
import { HorizonCoordinates, ObserverLocation } from '../astronomy/HorizonCoordinates';

/**
 * 专业级星场渲染器
 * 实现 StarWalk2 级别的星点渲染
 * - 屏幕像素尺寸锁定
 * - 星密度随 zoom 变化
 * - 大气消光
 */
export class ProStarfieldRenderer {
    private scene: THREE.Scene;
    private camera: THREE.Camera;
    private starPoints: THREE.Points | null = null;
    private starMaterial: THREE.ShaderMaterial;
    
    // 星表数据
    private allStars: Array<{
        star: StarMeta;
        azimuth: number;
        altitude: number;
        position: THREE.Vector3;
    }> = [];
    
    // 缩放相关
    private currentZoom = 1.0;
    private currentMagLimit = 5.0;  // 当前显示的最暗星等
    
    // 天球半径
    private readonly SKY_RADIUS = 1000;
    
    constructor(scene: THREE.Scene, camera: THREE.Camera) {
        this.scene = scene;
        this.camera = camera;
        
        // 创建星点材质（锁定屏幕像素）
        this.starMaterial = this.createPixelLockedStarMaterial();
    }
    
    /**
     * 创建像素锁定的星点材质
     */
    private createPixelLockedStarMaterial(): THREE.ShaderMaterial {
        return new THREE.ShaderMaterial({
            uniforms: {
                uTime: { value: 0 },
                uResolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
                uFOV: { value: 75 },
                uExposure: { value: 2.0 },
                uPixelRatio: { value: window.devicePixelRatio }
            },
            vertexShader: `
                attribute float aMagnitude;
                attribute vec3 aColor;
                attribute float aAltitude;  // 高度角，用于大气消光
                
                uniform vec2 uResolution;
                uniform float uFOV;
                uniform float uExposure;
                uniform float uPixelRatio;
                
                varying vec3 vColor;
                varying float vIntensity;
                varying float vMagnitude;
                varying float vAltitude;
                
                void main() {
                    vMagnitude = aMagnitude;
                    vAltitude = aAltitude;
                    
                    // 物理准确的星等转亮度
                    float intensity = pow(10.0, -0.4 * aMagnitude);
                    
                    // 大气消光（地平线附近变暗）
                    float extinction = 1.0;
                    if (aAltitude < 30.0) {
                        // 低于 30° 开始有大气影响
                        float airMass = 1.0 / max(0.1, sin(radians(aAltitude)));
                        extinction = exp(-0.15 * (airMass - 1.0));  // 简化消光公式
                    }
                    
                    vIntensity = intensity * extinction * uExposure;
                    
                    // 大气消光也影响颜色（低空偏黄）
                    vec3 atmosphericColor = aColor;
                    if (aAltitude < 20.0) {
                        float yellowShift = smoothstep(0.0, 20.0, aAltitude);
                        atmosphericColor = mix(vec3(1.0, 0.9, 0.7), aColor, yellowShift);
                    }
                    vColor = atmosphericColor;
                    
                    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                    gl_Position = projectionMatrix * mvPosition;
                    
                    // ⭐ 核心：锁定屏幕像素尺寸
                    // 星点大小不随距离变化，只随星等和 FOV
                    float baseSizePixels = pow(intensity, 0.7) * 8.0;  // 基础像素大小
                    float fovScale = 75.0 / uFOV;  // FOV 补偿（放大时点不变大）
                    
                    // 最终屏幕像素大小
                    float screenSize = baseSizePixels * fovScale * uPixelRatio;
                    
                    // 限制范围（亮星最大，暗星最小）
                    gl_PointSize = clamp(screenSize, 2.0 * uPixelRatio, 20.0 * uPixelRatio);
                }
            `,
            fragmentShader: `
                varying vec3 vColor;
                varying float vIntensity;
                varying float vMagnitude;
                varying float vAltitude;
                
                void main() {
                    vec2 coord = gl_PointCoord - vec2(0.5);
                    float dist = length(coord) * 2.0;
                    
                    if (dist > 1.0) discard;
                    
                    // ⭐ 核心：光晕用 alpha 渐变（不是放大点）
                    // 中心核心：完全不透明
                    float core = 1.0 - smoothstep(0.0, 0.25, dist);
                    
                    // 内光晕：快速衰减
                    float innerGlow = exp(-dist * 3.0) * 0.6;
                    
                    // 外光晕：极慢衰减（只有亮星明显）
                    float outerGlow = 0.0;
                    if (vMagnitude < 3.0) {
                        outerGlow = exp(-dist * 1.5) * 0.3 * (3.0 - vMagnitude);
                    }
                    
                    // 组合亮度（HDR）
                    float brightness = core + innerGlow + outerGlow;
                    float finalIntensity = brightness * vIntensity;
                    
                    // 颜色（HDR，亮星可以超过 1.0）
                    vec3 finalColor = vColor * finalIntensity;
                    
                    gl_FragColor = vec4(finalColor, finalIntensity);
                }
            `,
            transparent: true,
            depthWrite: false,
            depthTest: false,  // 星空永远在背景
            blending: THREE.AdditiveBlending
        });
    }
    
    /**
     * 加载星场
     */
    public loadStarField(
        stars: StarMeta[],
        observerLocation: ObserverLocation,
        localSiderealTime: number
    ): void {
        console.log('🌟 加载专业星场...');
        
        // 转换所有星星到地平坐标并保存
        this.allStars = [];
        
        stars.forEach(star => {
            const { altitude, azimuth } = HorizonCoordinates.equatorialToHorizon(
                star.equatorialCoordinate.rightAscension,
                star.equatorialCoordinate.declination,
                observerLocation.latitude,
                localSiderealTime
            );
            
            if (altitude < -5) return;  // 地平线以下不加载
            
            const position = HorizonCoordinates.horizonToVector3(
                altitude,
                azimuth,
                this.SKY_RADIUS
            );
            
            this.allStars.push({ star, azimuth, altitude, position });
        });
        
        console.log(`📊 总星数: ${this.allStars.length} 颗（地平线以上）`);
        
        // 初始渲染（默认星等）
        this.updateStarField(this.currentMagLimit);
    }
    
    /**
     * 更新星场（根据星等限制）
     */
    private updateStarField(magLimit: number): void {
        // 过滤可见星星
        const visibleStars = this.allStars.filter(s => s.star.magnitude <= magLimit);
        
        const positions: number[] = [];
        const magnitudes: number[] = [];
        const colors: number[] = [];
        const altitudes: number[] = [];
        
        visibleStars.forEach(({ star, position, altitude }) => {
            positions.push(position.x, position.y, position.z);
            magnitudes.push(star.magnitude);
            altitudes.push(altitude);
            
            const color = this.bvToRGB(star.bvColor);
            colors.push(color.r, color.g, color.b);
        });
        
        // 移除旧的星点
        if (this.starPoints) {
            this.scene.remove(this.starPoints);
            this.starPoints.geometry.dispose();
        }
        
        // 创建新的星点
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('aMagnitude', new THREE.Float32BufferAttribute(magnitudes, 1));
        geometry.setAttribute('aColor', new THREE.Float32BufferAttribute(colors, 3));
        geometry.setAttribute('aAltitude', new THREE.Float32BufferAttribute(altitudes, 1));
        
        this.starPoints = new THREE.Points(geometry, this.starMaterial);
        this.starPoints.frustumCulled = false;  // 星空永远可见
        this.scene.add(this.starPoints);
        
        console.log(`✨ 显示星星: ${visibleStars.length} 颗 (mag ≤ ${magLimit.toFixed(1)})`);
    }
    
    /**
     * 设置缩放（改变 FOV 和星等限制）
     */
    public setZoom(zoom: number, fov: number): void {
        this.currentZoom = zoom;
        
        // ⭐ 核心：根据 zoom 计算星等限制
        // zoom 越大，显示越暗的星
        let magLimit: number;
        if (zoom <= 1.0) {
            magLimit = 4.5;  // 默认视野：只显示较亮的星
        } else if (zoom <= 1.5) {
            magLimit = 5.5;  // 轻微放大
        } else if (zoom <= 2.0) {
            magLimit = 6.0;  // 中度放大
        } else if (zoom <= 2.5) {
            magLimit = 6.5;  // 较大放大
        } else {
            magLimit = 7.5;  // 最大放大：显示很暗的星
        }
        
        // 只有变化时才更新
        if (Math.abs(magLimit - this.currentMagLimit) > 0.1) {
            this.currentMagLimit = magLimit;
            this.updateStarField(magLimit);
        }
        
        // 更新材质 uniform
        this.starMaterial.uniforms.uFOV.value = fov;
        
        // 根据 zoom 调整曝光
        const exposure = 2.0 + (zoom - 1.0) * 0.5;  // zoom 越大，曝光越高
        this.starMaterial.uniforms.uExposure.value = exposure;
    }
    
    /**
     * B-V 色温转 RGB
     */
    private bvToRGB(bv: number): THREE.Color {
        let r: number, g: number, b: number;
        
        if (bv < 0) {
            r = 0.7; g = 0.8; b = 1.0;
        } else if (bv < 0.5) {
            const t = bv / 0.5;
            r = 0.8 + t * 0.2;
            g = 0.9 + t * 0.1;
            b = 1.0 - t * 0.1;
        } else if (bv < 1.0) {
            const t = (bv - 0.5) / 0.5;
            r = 1.0;
            g = 1.0 - t * 0.15;
            b = 0.9 - t * 0.25;
        } else if (bv < 1.5) {
            const t = (bv - 1.0) / 0.5;
            r = 1.0;
            g = 0.85 - t * 0.2;
            b = 0.65 - t * 0.25;
        } else {
            r = 1.0;
            g = 0.65;
            b = 0.4;
        }
        
        return new THREE.Color(r, g, b);
    }
    
    /**
     * 更新动画
     */
    public update(deltaTime: number): void {
        if (this.starMaterial) {
            this.starMaterial.uniforms.uTime.value += deltaTime;
        }
    }
    
    /**
     * 窗口大小调整
     */
    public resize(width: number, height: number): void {
        this.starMaterial.uniforms.uResolution.value.set(width, height);
        this.starMaterial.uniforms.uPixelRatio.value = window.devicePixelRatio;
    }
    
    /**
     * 获取统计信息
     */
    public getStats() {
        const visible = this.starPoints?.geometry.attributes.position.count || 0;
        return {
            totalStars: this.allStars.length,
            visibleStars: visible,
            currentMagLimit: this.currentMagLimit,
            currentZoom: this.currentZoom
        };
    }
    
    /**
     * 清理
     */
    public dispose(): void {
        if (this.starPoints) {
            this.starPoints.geometry.dispose();
            this.scene.remove(this.starPoints);
        }
        this.starMaterial.dispose();
    }
}
