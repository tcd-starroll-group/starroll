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
    
    // 手动控制
    private manualRotation = { x: 0, y: 0 };
    private isDragging = false;
    private lastMousePosition = { x: 0, y: 0 };
    private zoom = 1.0;  // 缩放级别
    
    // 标签管理
    private labelManager: StarLabelManager;
    
    constructor(container: HTMLElement) {
        this.container = container;
        
        // 创建场景
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000510); // 深蓝夜空
        
        // 创建相机（地面观测者视角）
        this.camera = new THREE.PerspectiveCamera(
            75,  // FOV
            window.innerWidth / window.innerHeight,
            0.1,
            this.SKY_RADIUS * 2
        );
        
        // 相机初始位置：地面，向上看（仰角45度）
        this.camera.position.set(0, 0, 0); // 观测者位置
        this.camera.lookAt(0, 1, 1); // 向北方天空看
        
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
        
        // 创建星座连线
        this.createConstellationLines();
        
        // 加载星座模型
        await this.loadConstellationModels();
            
            console.log('✅ 地面观测星空加载完成');
            
        } catch (error) {
            console.error('❌ 星空加载失败:', error);
        }
    }
    
    /**
     * 从星表创建星点（地平坐标）
     */
    private createStarFieldFromCatalog(stars: StarMeta[]): void {
        const geometry = new THREE.BufferGeometry();
        const positions: number[] = [];
        const magnitudes: number[] = [];
        const colors: number[] = [];
        
        let visibleCount = 0;
        
        stars.forEach(star => {
            if (star.magnitude > 6.5) return; // 只显示肉眼可见的星
            
            // 转换为地平坐标
            const { altitude, azimuth } = HorizonCoordinates.equatorialToHorizon(
                star.equatorialCoordinate.rightAscension,
                star.equatorialCoordinate.declination,
                this.observerLocation.latitude,
                this.localSiderealTime
            );
            
            // 只渲染地平线以上的星
            if (altitude < 0) return;
            
            // 转换为 3D 位置
            const pos = HorizonCoordinates.horizonToVector3(
                altitude,
                azimuth,
                this.SKY_RADIUS
            );
            
            positions.push(pos.x, pos.y, pos.z);
            magnitudes.push(star.magnitude);
            
            // B-V 颜色
            const color = this.bvToRGB(star.bvColor);
            colors.push(color.r, color.g, color.b);
            
            // 保存星星位置（用于连线）
            this.starMap.set(star.hIP, { star, position: pos });
            
            visibleCount++;
        });
        
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('aMagnitude', new THREE.Float32BufferAttribute(magnitudes, 1));
        geometry.setAttribute('aColor', new THREE.Float32BufferAttribute(colors, 3));
        
        const material = this.createStarMaterial();
        this.starPoints = new THREE.Points(geometry, material);
        this.scene.add(this.starPoints);
        
        console.log(`✨ 地平线以上可见恒星: ${visibleCount} 颗`);
        
        // 添加亮星标签
        const brightStarPositions = new Map<number, THREE.Vector3>();
        this.starMap.forEach((data, hip) => {
            if (data.star.magnitude <= 2.5) {  // 只标注 2.5 等以上的亮星
                brightStarPositions.set(hip, data.position);
            }
        });
        
        this.labelManager.addBrightStarLabels(brightStarPositions, 2.5);
        this.labelManager.addLabelsToScene(this.scene);
    }
    
    /**
     * 创建星点材质
     */
    private createStarMaterial(): THREE.ShaderMaterial {
        return new THREE.ShaderMaterial({
            uniforms: {
                uTime: { value: 0 },
                uExposure: { value: 4.0 },  // 大幅增加曝光（从 2.5 → 4.0）
                uPixelRatio: { value: window.devicePixelRatio },
                uBaseSize: { value: 120.0 }  // 基础大小系数
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
                    
                    // 大幅增大星点大小
                    // 使用更激进的缩放让星星非常明显
                    float baseSize = pow(intensity, 0.5) * uBaseSize;  // 从 60 增加到 120，指数从 0.6 降到 0.5
                    float size = baseSize * uPixelRatio;
                    
                    // 增大最小尺寸，确保所有星星都清晰可见
                    gl_PointSize = max(size, 8.0 * uPixelRatio);  // 从 3.0 增加到 8.0
                }
            `,
            fragmentShader: `
                varying vec3 vColor;
                varying float vIntensity;
                varying float vMagnitude;
                
                void main() {
                    vec2 coord = gl_PointCoord - vec2(0.5);
                    float dist = length(coord) * 2.0;  // 归一化到半径
                    
                    if (dist > 1.0) discard;
                    
                    // 更明显的光晕结构
                    // 核心：0-40% 半径，完全不透明
                    float core = 1.0 - smoothstep(0.0, 0.4, dist);
                    
                    // 内光晕：40%-70% 半径
                    float innerHalo = (1.0 - smoothstep(0.4, 0.7, dist)) * 0.6;
                    
                    // 外光晕：70%-100% 半径
                    float outerHalo = (1.0 - smoothstep(0.7, 1.0, dist)) * 0.3;
                    
                    // 组合亮度
                    float brightness = core + innerHalo + outerHalo;
                    
                    // 大幅增强星星亮度
                    float starBrightness = vIntensity;
                    
                    // 亮星有更强的增强
                    if (vMagnitude < 1.0) {
                        starBrightness *= 3.0;  // 0-1等星：3倍增强
                    } else if (vMagnitude < 2.0) {
                        starBrightness *= 2.5;  // 1-2等星：2.5倍增强
                    } else if (vMagnitude < 3.0) {
                        starBrightness *= 2.0;  // 2-3等星：2倍增强
                    } else {
                        starBrightness *= 1.5;  // 其他星：1.5倍增强
                    }
                    
                    float alpha = brightness * starBrightness;
                    
                    // HDR 颜色（亮星可以很亮）
                    vec3 finalColor = vColor * starBrightness * 1.5;  // 整体再增亮50%
                    
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
        console.log('✅ AR 模式已启用');
        console.log('📱 转动设备即可环顾星空');
        
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
        console.log('🛑 AR 模式已禁用');
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
        // 仰角: 0° = 地平线，90° = 天顶，-90° = 地下
        
        const azimuthRad = THREE.MathUtils.degToRad(azimuth);
        const altitudeRad = THREE.MathUtils.degToRad(altitude);
        
        // 计算相机朝向
        const direction = new THREE.Vector3(
            Math.sin(azimuthRad) * Math.cos(altitudeRad),  // X
            Math.sin(altitudeRad),                          // Y
            Math.cos(azimuthRad) * Math.cos(altitudeRad)   // Z
        );
        
        this.camera.lookAt(direction);
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
        
        // 更新星点闪烁
        if (this.starPoints && this.starPoints.material instanceof THREE.ShaderMaterial) {
            this.starPoints.material.uniforms.uTime.value += dt;
        }
        
        // 更新星座模型旋转
        this.constellationModels.children.forEach(model => {
            model.rotation.y += dt * 0.05;
            
            // 更新玻璃材质动画
            model.traverse((child: any) => {
                if (child.isMesh && child.material && child.material.uniforms && child.material.uniforms.uTime) {
                    child.material.uniforms.uTime.value += dt;
                }
            });
        });
        
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
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
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
}
