import * as THREE from 'three';
import type { StarMeta } from '../../types/star-meta';
import type { ConstellationModel } from '../data/constellation-models';
import { HorizonCoordinates, ObserverLocation, OBSERVER_LOCATIONS } from '../astronomy/HorizonCoordinates';
import { loadStarCatalog } from '../../types/star-catalog';
import { constellationModels, constellationLinesWithModels } from '../data/constellation-models';
import { ModelLoader } from '../utils/GLTFLoader';
import { GlassConstellationMaterial } from '../materials/ConstellationMaterials';
import { sensorManager, type SensorData, type CameraOrientation } from '../Tensors/sensor';
import { StarLabelManager } from './StarLabelManager';
import { getStarName, formatStarDisplayName } from '../data/star-names';

/**
 * 星星点击信息
 */
export interface StarClickInfo {
    hip: number;
    name: string;
    englishName: string;
    constellation: string;
    magnitude: number;
    bvColor: number;
    distance?: number;
    rightAscension: number;
    declination: number;
    altitude: number;
    azimuth: number;
}

/**
 * 地面观测者渲染器
 * 模拟从地球表面观测星空的视角
 */
export class GroundObserverRenderer {
    private scene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private renderer: THREE.WebGLRenderer;
    private container: HTMLElement;
    
    // 观测者参数
    private observerLocation: ObserverLocation = OBSERVER_LOCATIONS.SHANGHAI;
    private observationTime: Date = new Date();
    private localSiderealTime: number = 0;
    
    // 渲染对象
    private starPoints: THREE.Points | null = null;
    private ground: THREE.Mesh | null = null;
    private horizon: THREE.Line | null = null;
    private constellationModels: THREE.Group = new THREE.Group();
    private constellationLines: THREE.Group = new THREE.Group();
    
    // 星图数据
    private starMap: Map<number, { star: StarMeta, position: THREE.Vector3 }> = new Map();
    
    // 天球
    private readonly SKY_RADIUS = 1000;
    
    // 动画
    private animationFrameId: number | null = null;
    
    // AR 模式
    private arMode: boolean = false;
    private cameraOrientation: CameraOrientation | null = null;
    
    // 摄像头视频
    private videoElement: HTMLVideoElement | null = null;
    private videoStream: MediaStream | null = null;
    
    // 手动控制
    private manualRotation = { x: 0, y: 0 };
    private isDragging = false;
    private lastMousePosition = { x: 0, y: 0 };
    private zoom = 1.0;  // 缩放级别
    
    // 标签管理
    private labelManager: StarLabelManager;
    
    // 点击检测
    private raycaster: THREE.Raycaster = new THREE.Raycaster();
    private mouse: THREE.Vector2 = new THREE.Vector2();
    private onStarClickCallback: ((starInfo: StarClickInfo) => void) | null = null;
    
    // 地理位置状态
    private isRequestingLocation = false;
    private locationPermissionGranted = false;
    
    constructor(container: HTMLElement) {
        this.container = container;
        
        // 创建场景
        this.scene = new THREE.Scene();
        // 默认深色背景，AR模式时会改为透明
        this.scene.background = new THREE.Color(0x000510);
        
        // 创建相机（地面观测者视角）
        this.camera = new THREE.PerspectiveCamera(
            75,  // FOV - 保持75度（后续算法需要）
            window.innerWidth / window.innerHeight,
            0.1,
            this.SKY_RADIUS * 2
        );
        
        // 相机初始位置：地面中心（观测者位置）
        this.camera.position.set(0, 0, 0);
        this.camera.lookAt(0, 1, 0); // 初始向上看（天顶方向）
        
        // 创建渲染器
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true  // 为 AR 准备
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.0;
        container.appendChild(this.renderer.domElement);
        
        // 创建地面和地平线
        this.createGround();
        this.createHorizon();
        
        // 添加光照
        this.setupLighting();
        
        // 初始化标签管理器
        this.labelManager = new StarLabelManager(container);
        
        // 加载星空
        this.loadStarField();
        
        // 启动渲染
        this.animate();
        
        // 设置鼠标控制
        this.setupMouseControl();
        
        // 设置点击检测
        this.setupClickDetection();
        
        // 监听窗口大小
        window.addEventListener('resize', this.onWindowResize);
        
        console.log('🌍 地面观测者渲染器初始化完成');
        console.log(`📍 观测地点: ${this.observerLocation.name}`);
        console.log(`🧭 纬度: ${this.observerLocation.latitude}°`);
    }
    
    /**
     * 创建地面
     */
    private createGround(): void {
        // 地面平面（圆形）
        const geometry = new THREE.CircleGeometry(2000, 64);
        
        // 地面材质（深色，带微弱网格）
        const material = new THREE.ShaderMaterial({
            uniforms: {
                uColor: { value: new THREE.Color(0x0a0a15) }
            },
            vertexShader: `
                varying vec2 vUv;
                varying vec3 vPosition;
                void main() {
                    vUv = uv;
                    vPosition = position;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform vec3 uColor;
                varying vec2 vUv;
                varying vec3 vPosition;
                
                void main() {
                    // 距离衰减
                    float dist = length(vPosition);
                    float fade = 1.0 - smoothstep(1000.0, 2000.0, dist);
                    
                    // 微弱网格
                    float grid = 0.0;
                    float gridSize = 100.0;
                    if (mod(vPosition.x, gridSize) < 2.0 || mod(vPosition.y, gridSize) < 2.0) {
                        grid = 0.05;
                    }
                    
                    vec3 color = uColor + vec3(grid);
                    gl_FragColor = vec4(color, fade);
                }
            `,
            transparent: true,
            side: THREE.DoubleSide
        });
        
        this.ground = new THREE.Mesh(geometry, material);
        this.ground.rotation.x = -Math.PI / 2; // 水平放置
        this.ground.position.y = 0;
        this.scene.add(this.ground);
    }
    
    /**
     * 创建地平线
     */
    private createHorizon(): void {
        const points: THREE.Vector3[] = [];
        const segments = 128;
        const horizonRadius = 1500;
        
        for (let i = 0; i <= segments; i++) {
            const angle = (i / segments) * Math.PI * 2;
            const x = Math.cos(angle) * horizonRadius;
            const z = Math.sin(angle) * horizonRadius;
            points.push(new THREE.Vector3(x, 0, z));
        }
        
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
            color: 0x4488ff,
            transparent: true,
            opacity: 0.3
        });
        
        this.horizon = new THREE.Line(geometry, material);
        this.scene.add(this.horizon);
    }
    
    /**
     * 设置光照
     */
    private setupLighting(): void {
        // 微弱环境光（模拟星光和天光）
        const ambientLight = new THREE.AmbientLight(0x202040, 0.2);
        this.scene.add(ambientLight);
    }
    
    /**
     * 加载星空（地平坐标系）
     */
    private async loadStarField(): Promise<void> {
        try {
            console.log('🌟 加载地面观测星空...');
            
            // 加载星表
            const stars = await loadStarCatalog();
            
            // 计算本地恒星时
            this.localSiderealTime = HorizonCoordinates.calculateLocalSiderealTime(
                this.observerLocation.longitude,
                this.observationTime
            );
            
        // 转换为地平坐标并渲染
        this.createStarFieldFromCatalog(stars);
        
        // 暂时禁用星座连线和模型，专注于星星渲染
        // this.createConstellationLines();
        // await this.loadConstellationModels();
            
            console.log('✅ 地面观测星空加载完成（仅星星）');
            
        } catch (error) {
            console.error('❌ 星空加载失败:', error);
        }
    }
    
    /**
     * 从星表创建星点（地平坐标）- 使用不同纹理渲染不同亮度的星星
     */
    private createStarFieldFromCatalog(stars: StarMeta[]): void {
        // 按星等分组
        const brightStars: { pos: THREE.Vector3, color: THREE.Color, star: StarMeta }[] = [];  // < 1等
        const mediumStars: { pos: THREE.Vector3, color: THREE.Color, star: StarMeta }[] = [];  // 1-2.5等
        const dimStars: { pos: THREE.Vector3, color: THREE.Color, star: StarMeta }[] = [];     // 2.5-4.5等
        
        let totalCount = 0;
        
        stars.forEach(star => {
            if (star.magnitude > 4.5) return; // 只显示4.5等及以下
            
            // 转换为地平坐标
            const { altitude, azimuth } = HorizonCoordinates.equatorialToHorizon(
                star.equatorialCoordinate.rightAscension,
                star.equatorialCoordinate.declination,
                this.observerLocation.latitude,
                this.localSiderealTime
            );
            
            if (altitude < 0) return; // 只渲染地平线以上
            
            // 转换为 3D 位置
            const pos = HorizonCoordinates.horizonToVector3(altitude, azimuth, this.SKY_RADIUS);
            const color = this.bvToRGB(star.bvColor);
            
            // 保存星星位置
            this.starMap.set(star.hIP, { star, position: pos });
            
            // 按星等分组
            const starData = { pos, color, star };
            if (star.magnitude < 1.0) {
                brightStars.push(starData);
            } else if (star.magnitude < 2.5) {
                mediumStars.push(starData);
            } else {
                dimStars.push(starData);
            }
            
            totalCount++;
        });
        
        // 清除旧的星星
        if (this.starPoints) {
            this.scene.remove(this.starPoints);
        }
        
        // 创建星星组
        const starGroup = new THREE.Group();
        starGroup.name = 'Stars';
        
        // 1. 渲染极亮星（带光芒）- 使用 star16x16_ray.png
        if (brightStars.length > 0) {
            const points = this.createStarPoints(
                brightStars,
                '/texture/star16x16_ray.png',  // 带光芒的纹理
                8.0  // 较大
            );
            starGroup.add(points);
            console.log(`⭐ 极亮星 (<1等): ${brightStars.length} 颗`);
        }
        
        // 2. 渲染中等亮星 - 使用 star16x16.png
        if (mediumStars.length > 0) {
            const points = this.createStarPoints(
                mediumStars,
                '/texture/star16x16.png',  // 普通星点纹理
                5.0  // 中等大小
            );
            starGroup.add(points);
            console.log(`⭐ 中等亮星 (1-2.5等): ${mediumStars.length} 颗`);
        }
        
        // 3. 渲染暗星 - 使用 star16x16.png（更小）
        if (dimStars.length > 0) {
            const points = this.createStarPoints(
                dimStars,
                '/texture/star16x16.png',
                3.0  // 较小
            );
            starGroup.add(points);
            console.log(`⭐ 暗星 (2.5-4.5等): ${dimStars.length} 颗`);
        }
        
        this.starPoints = starGroup as any;  // 保存为组
        this.scene.add(starGroup);
        
        console.log(`✨ 地平线以上可见恒星: ${totalCount} 颗`);
    }
    
    /**
     * 创建星星点对象（使用程序化纹理 + 闪烁效果）
     */
    private createStarPoints(
        starsData: { pos: THREE.Vector3, color: THREE.Color, star: StarMeta }[],
        texturePath: string,
        baseSize: number
    ): THREE.Points {
        const positions: number[] = [];
        const colors: number[] = [];
        const magnitudes: number[] = [];
        const twinklePhases: number[] = [];  // 闪烁相位（随机）
        
        starsData.forEach(({ pos, color, star }) => {
            positions.push(pos.x, pos.y, pos.z);
            colors.push(color.r, color.g, color.b);
            magnitudes.push(star.magnitude);
            
            // 每个星星有随机的闪烁相位
            twinklePhases.push(Math.random() * Math.PI * 2);
        });
        
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        geometry.setAttribute('magnitude', new THREE.Float32BufferAttribute(magnitudes, 1));
        geometry.setAttribute('twinklePhase', new THREE.Float32BufferAttribute(twinklePhases, 1));
        
        // 使用Canvas动态生成完美的星星纹理（无黑边）
        const isRayTexture = texturePath.includes('ray');
        const texture = this.createProceduralStarTexture(isRayTexture);
        
        // 创建带闪烁效果的shader材质
        const material = this.createTwinkleStarMaterial(texture, baseSize);
        
        return new THREE.Points(geometry, material);
    }
    
    /**
     * 创建带闪烁效果的星星材质
     */
    private createTwinkleStarMaterial(texture: THREE.Texture, baseSize: number): THREE.ShaderMaterial {
        return new THREE.ShaderMaterial({
            uniforms: {
                uTexture: { value: texture },
                uSize: { value: baseSize },
                uTime: { value: 0 },
                uPixelRatio: { value: window.devicePixelRatio }
            },
            vertexShader: `
                attribute vec3 color;
                attribute float magnitude;
                attribute float twinklePhase;
                
                uniform float uSize;
                uniform float uTime;
                uniform float uPixelRatio;
                
                varying vec3 vColor;
                varying float vTwinkle;
                
                void main() {
                    vColor = color;
                    
                    // 计算闪烁效果
                    // 根据星等调整闪烁频率和幅度
                    float twinkleSpeed = 1.0 + magnitude * 0.3;  // 暗星闪得慢
                    float twinkleAmount = 0.15 + (6.0 - magnitude) * 0.05;  // 亮星闪得明显
                    
                    // 使用sin函数创建周期性闪烁
                    float twinkle = sin(uTime * twinkleSpeed + twinklePhase) * twinkleAmount;
                    vTwinkle = 1.0 + twinkle;  // 0.85 - 1.15 范围
                    
                    // 计算位置
                    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                    gl_Position = projectionMatrix * mvPosition;
                    
                    // 大小也随闪烁轻微变化
                    gl_PointSize = uSize * vTwinkle * uPixelRatio;
                }
            `,
            fragmentShader: `
                uniform sampler2D uTexture;
                
                varying vec3 vColor;
                varying float vTwinkle;
                
                void main() {
                    // 采样纹理
                    vec4 texColor = texture2D(uTexture, gl_PointCoord);
                    
                    // 应用星星颜色和闪烁
                    vec3 finalColor = texColor.rgb * vColor * vTwinkle;
                    float alpha = texColor.a;
                    
                    gl_FragColor = vec4(finalColor, alpha);
                }
            `,
            transparent: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
    }
    
    /**
     * 程序化创建星星纹理（完美的透明背景，无黑边）
     */
    private createProceduralStarTexture(withRays: boolean = false): THREE.CanvasTexture {
        const size = 128;
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d')!;
        
        // 清除画布（完全透明）
        ctx.clearRect(0, 0, size, size);
        
        const center = size / 2;
        
        if (withRays) {
            // 带光芒的星星（用于极亮星）
            ctx.save();
            ctx.translate(center, center);
            
            // 绘制十字光芒
            const rayLength = size * 0.45;
            const rayWidth = 2;
            
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.lineWidth = rayWidth;
            ctx.lineCap = 'round';
            
            // 四向光芒
            for (let i = 0; i < 4; i++) {
                ctx.rotate(Math.PI / 4);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(0, -rayLength);
                ctx.stroke();
                ctx.rotate(Math.PI / 4);
            }
            
            ctx.restore();
        }
        
        // 绘制中心发光球（所有星星都有）
        const gradient = ctx.createRadialGradient(center, center, 0, center, center, size / 2);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 1.0)');     // 中心纯白
        gradient.addColorStop(0.1, 'rgba(255, 255, 255, 1.0)');   // 核心
        gradient.addColorStop(0.3, 'rgba(255, 255, 255, 0.8)');   // 内光晕
        gradient.addColorStop(0.6, 'rgba(255, 255, 255, 0.4)');   // 中光晕
        gradient.addColorStop(0.8, 'rgba(255, 255, 255, 0.1)');   // 外光晕
        gradient.addColorStop(1.0, 'rgba(255, 255, 255, 0.0)');   // 边缘完全透明
        
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, size, size);
        
        // 创建纹理
        const texture = new THREE.CanvasTexture(canvas);
        texture.needsUpdate = true;
        
        return texture;
    }
    
    /**
     * 创建星点材质（单一纹理版本 - 备用）
     */
    private createStarMaterialSingle(texturePath: string = '/texture/star16x16.png'): THREE.PointsMaterial {
        const textureLoader = new THREE.TextureLoader();
        const starTexture = textureLoader.load(texturePath);
        
        return new THREE.PointsMaterial({
            size: 5.0,
            map: starTexture,
            transparent: true,
            opacity: 1.0,
            vertexColors: true,
            sizeAttenuation: false,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
    }
    
    /**
     * 创建星点材质（Shader版本 - 备用）
     */
    private createStarMaterialShader(): THREE.ShaderMaterial {
        return new THREE.ShaderMaterial({
            uniforms: {
                uTime: { value: 0 },
                uExposure: { value: 1.2 },
                uPixelRatio: { value: window.devicePixelRatio },
                uBaseSize: { value: 18.0 }
            },
            vertexShader: `
                attribute float aMagnitude;
                attribute vec3 aColor;
                uniform float uExposure;
                uniform float uPixelRatio;
                uniform float uBaseSize;
                
                varying vec3 vColor;
                varying float vIntensity;
                varying float vMagnitude;
                
                void main() {
                    vColor = aColor;
                    vMagnitude = aMagnitude;
                    
                    // 星等转亮度（增强对比度）
                    float intensity = pow(10.0, -0.4 * aMagnitude);
                    vIntensity = intensity * uExposure;
                    
                    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                    gl_Position = projectionMatrix * mvPosition;
                    
                    // 星点大小计算：根据亮度调整，创造更真实的星空效果
                    float baseSize = pow(intensity, 0.8) * uBaseSize;
                    float size = baseSize * uPixelRatio;
                    
                    // 最小尺寸确保星星可见
                    gl_PointSize = max(size, 1.5 * uPixelRatio);
                }
            `,
            fragmentShader: `
                varying vec3 vColor;
                varying float vIntensity;
                varying float vMagnitude;
                
                void main() {
                    vec2 coord = gl_PointCoord - vec2(0.5);
                    float dist = length(coord) * 2.0;
                    
                    if (dist > 1.0) discard;
                    
                    // 精细的星星光晕效果
                    // 核心：0-30% 半径，高亮中心
                    float core = 1.0 - smoothstep(0.0, 0.3, dist);
                    core = pow(core, 0.5);  // 更锐利的中心
                    
                    // 内光晕：30%-60% 半径
                    float innerHalo = (1.0 - smoothstep(0.3, 0.6, dist)) * 0.5;
                    
                    // 外光晕：60%-100% 半径，轻微扩散
                    float outerHalo = (1.0 - smoothstep(0.6, 1.0, dist)) * 0.2;
                    
                    // 组合亮度
                    float brightness = core + innerHalo + outerHalo;
                    
                    // 适度增强亮星
                    float starBrightness = vIntensity;
                    
                    // 对亮星进行适度增强
                    if (vMagnitude < 1.0) {
                        starBrightness *= 1.8;  // 0-1等星：1.8倍
                    } else if (vMagnitude < 2.0) {
                        starBrightness *= 1.5;  // 1-2等星：1.5倍
                    } else if (vMagnitude < 3.0) {
                        starBrightness *= 1.3;  // 2-3等星：1.3倍
                    } else {
                        starBrightness *= 1.1;  // 其他星：1.1倍
                    }
                    
                    float alpha = brightness * starBrightness;
                    
                    // 自然的星光颜色
                    vec3 finalColor = vColor * starBrightness;
                    
                    gl_FragColor = vec4(finalColor, alpha);
                }
            `,
            transparent: true,
            depthWrite: false,
            blending: THREE.AdditiveBlending
        });
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
     * 创建星座连线（地平坐标）
     */
    private createConstellationLines(): void {
        console.log('🔗 创建星座连线（地平坐标）...');
        
        this.constellationLines.name = 'ConstellationLines';
        this.scene.add(this.constellationLines);
        
        let totalLines = 0;
        
        constellationLinesWithModels.forEach(constellation => {
            const lineGroup = new THREE.Group();
            lineGroup.name = constellation.id;
            
            const positions: number[] = [];
            
            constellation.lines.forEach(([hip1, hip2]) => {
                const star1 = this.starMap.get(hip1);
                const star2 = this.starMap.get(hip2);
                
                if (star1 && star2) {
                    positions.push(
                        star1.position.x, star1.position.y, star1.position.z,
                        star2.position.x, star2.position.y, star2.position.z
                    );
                }
            });
            
            if (positions.length > 0) {
                const geometry = new THREE.BufferGeometry();
                geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
                
                const material = new THREE.LineBasicMaterial({
                    color: 0x4488ff,
                    transparent: true,
                    opacity: 0.4,
                    linewidth: 1
                });
                
                const lines = new THREE.LineSegments(geometry, material);
                lineGroup.add(lines);
                
                totalLines += positions.length / 6;
            }
            
            this.constellationLines.add(lineGroup);
        });
        
        console.log(`✅ 创建了 ${totalLines} 条星座连线`);
    }
    
    /**
     * 加载星座模型（地平坐标）
     */
    private async loadConstellationModels(): Promise<void> {
        console.log('🎭 加载星座 3D 模型（地平坐标）...');
        
        this.constellationModels.name = 'Constellations';
        this.scene.add(this.constellationModels);
        
        // 加载真实星表以获取中心恒星位置
        const stars = await loadStarCatalog();
        const starMap = new Map<number, StarMeta>();
        stars.forEach(s => starMap.set(s.hIP, s));
        
        const loadPromises = constellationModels.map(async (config) => {
            try {
                if (!config.centerHIP) return;
                
                const centerStar = starMap.get(config.centerHIP);
                if (!centerStar) {
                    console.warn(`未找到中心恒星 HIP ${config.centerHIP}`);
                    return;
                }
                
                // 转换为地平坐标
                const { altitude, azimuth } = HorizonCoordinates.equatorialToHorizon(
                    centerStar.equatorialCoordinate.rightAscension,
                    centerStar.equatorialCoordinate.declination,
                    this.observerLocation.latitude,
                    this.localSiderealTime
                );
                
                // 只加载地平线以上的星座
                if (altitude < 0) {
                    console.log(`  ⏸️ ${config.name} 在地平线以下，跳过`);
                    return;
                }
                
                // 加载模型
                const model = await ModelLoader.loadModel(config.modelPath);
                
                // 计算位置
                const position = HorizonCoordinates.horizonToVector3(
                    altitude,
                    azimuth,
                    this.SKY_RADIUS * 0.95
                );
                
                model.position.copy(position);
                model.lookAt(0, 0, 0); // 面向观测者
                model.scale.setScalar(config.scale || 50);
                
                // 应用玻璃材质
                this.applyGlassMaterial(model);
                
                model.name = config.id;
                model.userData = {
                    constellationId: config.id,
                    constellationName: config.name,
                    altitude: altitude,
                    azimuth: azimuth
                };
                
                this.constellationModels.add(model);
                
                console.log(`  ✅ ${config.name} (高度: ${altitude.toFixed(1)}°, 方位: ${azimuth.toFixed(1)}°)`);
                
            } catch (error) {
                console.error(`  ❌ ${config.name} 加载失败:`, error);
            }
        });
        
        await Promise.all(loadPromises);
        console.log(`🎉 星座模型加载完成！可见: ${this.constellationModels.children.length} 个`);
    }
    
    /**
     * 应用玻璃材质
     */
    private applyGlassMaterial(model: THREE.Group): void {
        model.traverse((child: any) => {
            if (child.isMesh) {
                const glassMaterial = GlassConstellationMaterial.clone();
                child.material = glassMaterial;
                child.material.needsUpdate = true;
            }
        });
    }
    
    /**
     * 设置鼠标控制（桌面端）
     */
    private setupMouseControl(): void {
        this.renderer.domElement.addEventListener('mousedown', (e) => {
            if (this.arMode) return; // AR 模式下禁用鼠标控制
            
            this.isDragging = true;
            this.lastMousePosition = { x: e.clientX, y: e.clientY };
        });
        
        this.renderer.domElement.addEventListener('mousemove', (e) => {
            if (!this.isDragging || this.arMode) return;
            
            const deltaX = e.clientX - this.lastMousePosition.x;
            const deltaY = e.clientY - this.lastMousePosition.y;
            
            this.manualRotation.y += deltaX * 0.005; // 左右旋转（方位角）
            this.manualRotation.x -= deltaY * 0.005; // 上下旋转（仰角）
            
            // 限制仰角范围（-90° 到 90°）
            this.manualRotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, this.manualRotation.x));
            
            this.lastMousePosition = { x: e.clientX, y: e.clientY };
            
            this.updateCameraFromManual();
        });
        
        this.renderer.domElement.addEventListener('mouseup', () => {
            this.isDragging = false;
        });
        
        this.renderer.domElement.addEventListener('mouseleave', () => {
            this.isDragging = false;
        });
        
        // 添加滚轮缩放
        this.renderer.domElement.addEventListener('wheel', (e) => {
            e.preventDefault();
            
            const zoomSpeed = 0.001;
            this.zoom += e.deltaY * -zoomSpeed;
            this.zoom = Math.max(0.5, Math.min(3.0, this.zoom));  // 限制缩放范围 0.5x - 3x
            
            // 更新相机 FOV 实现缩放
            this.camera.fov = 75 / this.zoom;
            this.camera.updateProjectionMatrix();
            
            // 同时更新星点大小
            if (this.starPoints && this.starPoints.material instanceof THREE.ShaderMaterial) {
                this.starPoints.material.uniforms.uBaseSize.value = 120.0 * this.zoom;
            }
            
            console.log(`🔍 缩放: ${this.zoom.toFixed(2)}x`);
        }, { passive: false });
        
        // 触摸缩放（移动端）
        let touchDistance = 0;
        this.renderer.domElement.addEventListener('touchstart', (e) => {
            if (e.touches.length === 2) {
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                touchDistance = Math.sqrt(dx * dx + dy * dy);
            }
        });
        
        this.renderer.domElement.addEventListener('touchmove', (e) => {
            if (e.touches.length === 2 && touchDistance > 0) {
                e.preventDefault();
                
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                const newDistance = Math.sqrt(dx * dx + dy * dy);
                
                const zoomDelta = (newDistance - touchDistance) * 0.01;
                this.zoom += zoomDelta;
                this.zoom = Math.max(0.5, Math.min(3.0, this.zoom));
                
                this.camera.fov = 75 / this.zoom;
                this.camera.updateProjectionMatrix();
                
                if (this.starPoints && this.starPoints.material instanceof THREE.ShaderMaterial) {
                    this.starPoints.material.uniforms.uBaseSize.value = 120.0 * this.zoom;
                }
                
                touchDistance = newDistance;
            }
        }, { passive: false });
        
        console.log('🖱️ 鼠标控制已设置（支持缩放）');
    }
    
    /**
     * 启用 AR 模式
     */
    public async enableARMode(): Promise<boolean> {
        console.log('📱 启用 AR 模式...');
        
        // 检查设备支持
        if (typeof DeviceOrientationEvent === 'undefined') {
            console.error('❌ 设备不支持方向传感器');
            return false;
        }
        
        // 请求权限（iOS）
        const permission = await sensorManager.requestPermission();
        if (permission === 'denied') {
            console.error('❌ 传感器权限被拒绝');
            return false;
        }
        
        // 添加传感器监听
        sensorManager.addListener(this.handleSensorData);
        sensorManager.startListening();
        
        this.arMode = true;
        
        // 启用透明背景（显示摄像头画面）
        this.scene.background = null;
        
        // 隐藏地面和地平线（AR模式不需要）
        if (this.ground) this.ground.visible = false;
        if (this.horizon) this.horizon.visible = false;
        
        // 启动摄像头
        await this.startCamera();
        
        console.log('✅ AR 模式已启用');
        console.log('📱 转动设备即可环顾星空');
        console.log('📷 摄像头已启动');
        
        return true;
    }
    
    /**
     * 禁用 AR 模式
     */
    public disableARMode(): void {
        if (!this.arMode) return;
        
        sensorManager.removeListener(this.handleSensorData);
        sensorManager.stopListening();
        
        this.arMode = false;
        
        // 停止摄像头
        this.stopCamera();
        
        // 恢复深色背景
        this.scene.background = new THREE.Color(0x000510);
        
        // 恢复地面和地平线
        if (this.ground) this.ground.visible = true;
        if (this.horizon) this.horizon.visible = true;
        
        console.log('🛑 AR 模式已禁用');
        console.log('📷 摄像头已关闭');
    }
    
    /**
     * 处理传感器数据
     */
    private handleSensorData = (data: SensorData): void => {
        if (!this.arMode) return;
        
        // 计算相机朝向
        const orientation = sensorManager.getCameraOrientation(data);
        if (!orientation) return;
        
        this.cameraOrientation = orientation;
        this.updateCameraFromSensor();
    };
    
    /**
     * 根据传感器更新相机（AR 模式）
     */
    private updateCameraFromSensor(): void {
        if (!this.cameraOrientation) return;
        
        const { azimuth, altitude } = this.cameraOrientation;
        
        // 将方位角和仰角转换为相机旋转
        // 方位角: 0° = 北，90° = 东，180° = 南，270° = 西
        // 仰角: 0° = 地平线，90° = 天顶，-90° = 天底
        
        const azimuthRad = THREE.MathUtils.degToRad(azimuth);
        const altitudeRad = THREE.MathUtils.degToRad(altitude);
        
        // 计算相机朝向的目标点（足够远的点）
        const distance = this.SKY_RADIUS;
        const target = new THREE.Vector3(
            Math.sin(azimuthRad) * Math.cos(altitudeRad) * distance,  // X
            Math.sin(altitudeRad) * distance,                          // Y
            Math.cos(azimuthRad) * Math.cos(altitudeRad) * distance   // Z
        );
        
        // 重置相机位置到原点，然后看向目标点
        this.camera.position.set(0, 0, 0);
        this.camera.lookAt(target);
        this.camera.updateProjectionMatrix();
    }
    
    /**
     * 根据手动控制更新相机（桌面模式）
     */
    private updateCameraFromManual(): void {
        // 使用欧拉角设置相机旋转
        const euler = new THREE.Euler(
            this.manualRotation.x,  // 俯仰
            this.manualRotation.y,  // 偏航
            0,                       // 翻滚
            'YXZ'
        );
        
        this.camera.rotation.copy(euler);
    }
    
    /**
     * 渲染循环
     */
    private animate = () => {
        const dt = 0.016;
        
        // 更新星点闪烁效果
        const time = Date.now() * 0.001;  // 当前时间（秒）
        
        if (this.starPoints) {
            this.starPoints.traverse((child: any) => {
                if (child instanceof THREE.Points && child.material instanceof THREE.ShaderMaterial) {
                    // 更新时间uniform，驱动闪烁动画
                    child.material.uniforms.uTime.value = time;
                }
            });
        }
        
        // 暂时禁用星座模型动画
        // this.constellationModels.children.forEach(model => {
        //     model.rotation.y += dt * 0.05;
        //     model.traverse((child: any) => {
        //         if (child.isMesh && child.material && child.material.uniforms && child.material.uniforms.uTime) {
        //             child.material.uniforms.uTime.value += dt;
        //         }
        //     });
        // });
        
        // 渲染
        this.renderer.render(this.scene, this.camera);
        
        // 渲染标签
        this.labelManager.render(this.scene, this.camera);
        
        this.animationFrameId = requestAnimationFrame(this.animate);
    };
    
    /**
     * 设置观测地点
     */
    public setObserverLocation(location: ObserverLocation): void {
        this.observerLocation = location;
        console.log(`📍 切换观测地点: ${location.name || '自定义地点'}`);
        console.log(`🧭 纬度: ${location.latitude}°, 经度: ${location.longitude}°`);
        
        // 重新加载星空
        this.loadStarField();
    }
    
    /**
     * 设置观测时间
     */
    public setObservationTime(time: Date): void {
        this.observationTime = time;
        console.log(`🕐 设置观测时间: ${time.toLocaleString()}`);
        
        // 重新计算星空
        this.loadStarField();
    }
    
    /**
     * 获取统计信息
     */
    public getStats() {
        const starCount = this.starPoints?.geometry.attributes.position.count || 0;
        const constellationCount = this.constellationModels.children.length;
        
        return {
            visibleStars: starCount,
            visibleConstellations: constellationCount,
            observerLocation: this.observerLocation.name,
            localSiderealTime: this.localSiderealTime.toFixed(2),
            arMode: this.arMode,
            sensorPermission: sensorManager.getPermissionState()
        };
    }
    
    /**
     * 获取当前相机朝向（用于调试）
     */
    public getCameraOrientation(): { azimuth: number, altitude: number } {
        // 从相机旋转计算方位角和仰角
        const direction = new THREE.Vector3(0, 0, 1);
        direction.applyQuaternion(this.camera.quaternion);
        
        const azimuth = Math.atan2(direction.x, direction.z) * 180 / Math.PI;
        const altitude = Math.asin(direction.y) * 180 / Math.PI;
        
        return {
            azimuth: ((azimuth % 360) + 360) % 360,
            altitude: altitude
        };
    }
    
    /**
     * 是否处于 AR 模式
     */
    public isARMode(): boolean {
        return this.arMode;
    }
    
    /**
     * 窗口大小调整
     */
    private onWindowResize = () => {
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        console.log(`📐 窗口调整: ${width}x${height}, aspect: ${this.camera.aspect.toFixed(2)}`);
    };
    
    /**
     * 清理
     */
    public dispose(): void {
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
        
        // 停止传感器监听
        if (this.arMode) {
            this.disableARMode();
        }
        
        window.removeEventListener('resize', this.onWindowResize);
        
        if (this.starPoints) {
            this.starPoints.geometry.dispose();
            if (this.starPoints.material instanceof THREE.Material) {
                this.starPoints.material.dispose();
            }
        }
        
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
        
        // 清理标签
        this.labelManager.dispose();
        
        this.renderer.dispose();
        this.container.removeChild(this.renderer.domElement);
    }
    
    /**
     * 设置星座连线可见性
     */
    public setConstellationLinesVisible(visible: boolean): void {
        this.constellationLines.visible = visible;
    }
    
    /**
     * 设置星星标签可见性
     */
    public setStarLabelsVisible(visible: boolean): void {
        this.labelManager.setLabelsVisible(visible);
    }
    
    /**
     * 设置星星点击回调
     */
    public setOnStarClick(callback: (starInfo: StarClickInfo) => void): void {
        this.onStarClickCallback = callback;
    }
    
    /**
     * 设置点击检测
     */
    private setupClickDetection(): void {
        // 配置 raycaster 参数 - 增大阈值让点击更容易
        this.raycaster.params.Points = {
            threshold: 5.0  // 点击检测阈值（世界坐标单位），增大以便更容易点击
        };
        
        const handleClick = (clientX: number, clientY: number) => {
            // 归一化鼠标坐标 (-1 到 +1)
            this.mouse.x = (clientX / window.innerWidth) * 2 - 1;
            this.mouse.y = -(clientY / window.innerHeight) * 2 + 1;
            
            // 更新射线
            this.raycaster.setFromCamera(this.mouse, this.camera);
            
            // 检测星点
            if (this.starPoints) {
                const intersects = this.raycaster.intersectObject(this.starPoints);
                
                if (intersects.length > 0) {
                    const intersection = intersects[0];
                    const index = intersection.index;
                    
                    if (index !== undefined) {
                        this.handleStarClick(index);
                    }
                }
            }
        };
        
        // 鼠标点击
        this.renderer.domElement.addEventListener('click', (e) => {
            if (this.isDragging) return; // 拖拽时不触发点击
            handleClick(e.clientX, e.clientY);
        });
        
        // 触摸点击（移动端）
        this.renderer.domElement.addEventListener('touchend', (e) => {
            if (e.changedTouches.length > 0) {
                const touch = e.changedTouches[0];
                handleClick(touch.clientX, touch.clientY);
            }
        });
    }
    
    /**
     * 处理星星点击
     */
    private handleStarClick(pointIndex: number): void {
        // 从 starMap 中找到对应的星星
        let clickedStar: { star: StarMeta, position: THREE.Vector3 } | undefined;
        let starIndex = 0;
        
        for (const [hip, starData] of this.starMap.entries()) {
            if (starIndex === pointIndex) {
                clickedStar = starData;
                break;
            }
            starIndex++;
        }
        
        if (!clickedStar) return;
        
        const star = clickedStar.star;
        
        // 获取星星名称
        const starName = getStarName(star.hIP);
        
        // 计算当前的地平坐标
        const { altitude, azimuth } = HorizonCoordinates.equatorialToHorizon(
            star.equatorialCoordinate.rightAscension,
            star.equatorialCoordinate.declination,
            this.observerLocation.latitude,
            this.localSiderealTime
        );
        
        // 构建星星信息
        const starInfo: StarClickInfo = {
            hip: star.hIP,
            name: starName?.chinese || `HIP ${star.hIP}`,
            englishName: starName?.english || '',
            constellation: starName?.constellation || '未知星座',
            magnitude: star.magnitude,
            bvColor: star.bvColor,
            distance: star.distance,
            rightAscension: star.equatorialCoordinate.rightAscension,
            declination: star.equatorialCoordinate.declination,
            altitude: altitude,
            azimuth: azimuth
        };
        
        console.log('⭐ 点击星星:', starInfo.name, starInfo);
        
        // 触觉反馈
        if (navigator.vibrate) {
            navigator.vibrate(30);
        }
        
        // 调用回调
        if (this.onStarClickCallback) {
            this.onStarClickCallback(starInfo);
        }
    }
    
    /**
     * 请求用户的地理位置
     * @returns Promise<ObserverLocation | null>
     */
    public async requestUserLocation(): Promise<ObserverLocation | null> {
        if (this.isRequestingLocation) {
            console.log('⏳ 正在请求地理位置...');
            return null;
        }
        
        if (!('geolocation' in navigator)) {
            console.error('❌ 浏览器不支持地理位置API');
            return null;
        }
        
        this.isRequestingLocation = true;
        
        try {
            console.log('📍 请求用户地理位置...');
            
            const position = await new Promise<GeolocationPosition>((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(
                    resolve,
                    reject,
                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0
                    }
                );
            });
            
            const { latitude, longitude } = position.coords;
            
            console.log(`✅ 获取到位置: ${latitude.toFixed(4)}°N, ${longitude.toFixed(4)}°E`);
            console.log(`📏 精度: ${position.coords.accuracy.toFixed(0)}米`);
            
            this.locationPermissionGranted = true;
            
            // 创建自定义观测位置
            const userLocation: ObserverLocation = {
                name: '当前位置',
                latitude: latitude,
                longitude: longitude
            };
            
            // 自动更新观测位置
            this.setObserverLocation(userLocation);
            
            return userLocation;
            
        } catch (error: any) {
            console.error('❌ 获取位置失败:', error.message);
            
            if (error.code === 1) {
                console.log('用户拒绝了位置权限');
            } else if (error.code === 2) {
                console.log('位置信息不可用');
            } else if (error.code === 3) {
                console.log('获取位置超时');
            }
            
            return null;
            
        } finally {
            this.isRequestingLocation = false;
        }
    }
    
    /**
     * 获取位置权限状态
     */
    public getLocationPermissionState(): 'granted' | 'prompt' | 'denied' {
        if (this.locationPermissionGranted) {
            return 'granted';
        }
        return 'prompt';
    }
    
    /**
     * 自动使用当前时间和位置
     */
    public async useCurrentLocationAndTime(): Promise<boolean> {
        console.log('🌍 使用当前位置和时间...');
        
        // 设置当前时间
        this.setObservationTime(new Date());
        
        // 请求位置
        const location = await this.requestUserLocation();
        
        return location !== null;
    }
    
    /**
     * 启动摄像头
     */
    private async startCamera(): Promise<void> {
        try {
            console.log('📷 正在启动摄像头...');
            
            // 创建video元素
            if (!this.videoElement) {
                this.videoElement = document.createElement('video');
                this.videoElement.setAttribute('playsinline', '');
                this.videoElement.setAttribute('webkit-playsinline', '');
                this.videoElement.style.position = 'fixed';
                this.videoElement.style.top = '0';
                this.videoElement.style.left = '0';
                this.videoElement.style.width = '100%';
                this.videoElement.style.height = '100%';
                this.videoElement.style.objectFit = 'cover';
                this.videoElement.style.zIndex = '-1';
                this.videoElement.style.pointerEvents = 'none';
                
                // 添加到容器
                this.container.appendChild(this.videoElement);
            }
            
            // 请求摄像头权限
            const constraints = {
                video: {
                    facingMode: 'environment',  // 后置摄像头
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                },
                audio: false
            };
            
            this.videoStream = await navigator.mediaDevices.getUserMedia(constraints);
            this.videoElement.srcObject = this.videoStream;
            
            // 播放视频
            await this.videoElement.play();
            
            console.log('✅ 摄像头已启动');
            console.log(`📹 分辨率: ${this.videoElement.videoWidth}x${this.videoElement.videoHeight}`);
            
        } catch (error: any) {
            console.error('❌ 摄像头启动失败:', error);
            
            if (error.name === 'NotAllowedError') {
                console.log('用户拒绝了摄像头权限');
            } else if (error.name === 'NotFoundError') {
                console.log('未找到摄像头设备');
            } else if (error.name === 'NotReadableError') {
                console.log('摄像头被其他应用占用');
            }
            
            throw error;
        }
    }
    
    /**
     * 停止摄像头
     */
    private stopCamera(): void {
        console.log('📷 正在关闭摄像头...');
        
        // 停止视频流
        if (this.videoStream) {
            this.videoStream.getTracks().forEach(track => {
                track.stop();
            });
            this.videoStream = null;
        }
        
        // 移除video元素
        if (this.videoElement) {
            this.videoElement.srcObject = null;
            if (this.videoElement.parentNode) {
                this.videoElement.parentNode.removeChild(this.videoElement);
            }
            this.videoElement = null;
        }
        
        console.log('✅ 摄像头已关闭');
    }
}
