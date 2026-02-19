import * as THREE from 'three';
import { SkyRootManager } from './SkyRootManager';
import { ProStarfieldRenderer } from './ProStarfieldRenderer';
import { TelescopeCamera } from './TelescopeCamera';
import { StarLabelManager } from './StarLabelManager';
import { ObserverLocation, OBSERVER_LOCATIONS, HorizonCoordinates } from '../astronomy/HorizonCoordinates';
import { loadStarCatalog } from '../../types/star-catalog';
import { constellationModels, constellationLinesWithModels } from '../data/constellation-models';
import type { StarMeta } from '../../types/star-meta';
import { ModelLoader } from '../utils/GLTFLoader';
import { sensorManager, type SensorData } from '../Tensors/sensor';

/**
 * StarWalk2 级别渲染器
 * 完整实现专业天文可视化架构
 */
export class StarWalk2Renderer {
    // 核心渲染
    private scene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private renderer: THREE.WebGLRenderer;
    private container: HTMLElement;
    
    // 分层系统
    private groundLayer: THREE.Group;           // 地面层
    private skyRootManager: SkyRootManager;     // 天空根节点管理器
    private starfieldRenderer: ProStarfieldRenderer;  // 专业星场
    private labelManager: StarLabelManager;     // 标签管理
    
    // 相机控制
    private telescopeCamera: TelescopeCamera;
    
    // 观测参数
    private observerLocation: ObserverLocation = OBSERVER_LOCATIONS.SHANGHAI;
    private observationTime: Date = new Date();
    private localSiderealTime: number = 0;
    
    // AR 模式
    private arMode = false;
    
    // 动画
    private animationFrameId: number | null = null;
    
    // 星表数据
    private starMap: Map<number, { star: StarMeta, position: THREE.Vector3 }> = new Map();
    
    constructor(container: HTMLElement) {
        this.container = container;
        
        console.log('🎬 初始化 StarWalk2 级别渲染器');
        console.log('📐 架构: Ground → Sky Dome → Starfield → Overlay');
        
        // 创建场景
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000510);
        
        // 创建相机
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            10000
        );
        
        // 创建渲染器（高质量）
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.0;
        container.appendChild(this.renderer.domElement);
        
        // 初始化望远镜相机控制
        this.telescopeCamera = new TelescopeCamera(this.camera, this.renderer.domElement);
        
        // 创建地面层
        this.groundLayer = new THREE.Group();
        this.groundLayer.name = 'Ground';
        this.scene.add(this.groundLayer);
        this.createGround();
        
        // 创建 SkyRoot 管理器
        this.skyRootManager = new SkyRootManager();
        this.skyRootManager.addToScene(this.scene);
        
        // 创建专业星场渲染器
        this.starfieldRenderer = new ProStarfieldRenderer(
            this.skyRootManager.starfieldLayer,
            this.camera
        );
        
        // 创建标签管理器
        this.labelManager = new StarLabelManager(container);
        
        // 设置光照
        this.setupLighting();
        
        // 加载数据
        this.loadAllData();
        
        // 连接缩放回调
        this.telescopeCamera.setOnZoomChange((zoom, fov) => {
            this.starfieldRenderer.setZoom(zoom, fov);
        });
        
        // 启动渲染
        this.animate();
        
        // 监听窗口大小
        window.addEventListener('resize', this.onWindowResize);
        
        console.log('✅ StarWalk2 渲染器初始化完成');
    }
    
    /**
     * 创建地面
     */
    private createGround(): void {
        // 地面圆形平面
        const groundGeometry = new THREE.CircleGeometry(3000, 64);
        const groundMaterial = new THREE.MeshBasicMaterial({
            color: 0x0a0a15,
            transparent: true,
            opacity: 0.9,
            side: THREE.DoubleSide
        });
        
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = 0;
        this.groundLayer.add(ground);
        
        // 地平线
        const horizonPoints: THREE.Vector3[] = [];
        for (let i = 0; i <= 128; i++) {
            const angle = (i / 128) * Math.PI * 2;
            horizonPoints.push(new THREE.Vector3(
                Math.cos(angle) * 2000,
                0.5,
                Math.sin(angle) * 2000
            ));
        }
        
        const horizonGeometry = new THREE.BufferGeometry().setFromPoints(horizonPoints);
        const horizonMaterial = new THREE.LineBasicMaterial({
            color: 0x4488ff,
            transparent: true,
            opacity: 0.4,
            linewidth: 2
        });
        
        const horizon = new THREE.Line(horizonGeometry, horizonMaterial);
        this.groundLayer.add(horizon);
    }
    
    /**
     * 设置光照
     */
    private setupLighting(): void {
        const ambient = new THREE.AmbientLight(0x202040, 0.3);
        this.scene.add(ambient);
    }
    
    /**
     * 加载所有数据
     */
    private async loadAllData(): Promise<void> {
        try {
            console.log('📂 加载星空数据...');
            
            // 计算本地恒星时
            this.localSiderealTime = HorizonCoordinates.calculateLocalSiderealTime(
                this.observerLocation.longitude,
                this.observationTime
            );
            
            // 加载星表
            const stars = await loadStarCatalog();
            
            // 加载星场
            this.starfieldRenderer.loadStarField(
                stars,
                this.observerLocation,
                this.localSiderealTime
            );
            
            // 加载星座（Overlay 层）
            await this.loadConstellationOverlay(stars);
            
            console.log('✅ 所有数据加载完成');
            
        } catch (error) {
            console.error('❌ 数据加载失败:', error);
        }
    }
    
    /**
     * 加载星座 Overlay 层
     */
    private async loadConstellationOverlay(stars: StarMeta[]): Promise<void> {
        console.log('🎭 加载星座 Overlay 层...');
        
        // 构建星图
        const starMap = new Map<number, { star: StarMeta, position: THREE.Vector3 }>();
        
        stars.forEach(star => {
            const { altitude, azimuth } = HorizonCoordinates.equatorialToHorizon(
                star.equatorialCoordinate.rightAscension,
                star.equatorialCoordinate.declination,
                this.observerLocation.latitude,
                this.localSiderealTime
            );
            
            if (altitude < 0) return;
            
            const position = HorizonCoordinates.horizonToVector3(
                altitude,
                azimuth,
                1000
            );
            
            starMap.set(star.hIP, { star, position });
        });
        
        // 创建星座连线
        this.createConstellationLines(starMap);
        
        // 加载星座模型
        await this.loadConstellationModels(starMap);
        
        // 添加亮星标签
        const brightStars = new Map<number, THREE.Vector3>();
        starMap.forEach((data, hip) => {
            if (data.star.magnitude <= 2.5) {
                brightStars.set(hip, data.position);
            }
        });
        this.labelManager.addBrightStarLabels(brightStars);
        this.labelManager.addLabelsToScene(this.skyRootManager.overlayLayer);
    }
    
    /**
     * 创建星座连线（Overlay 层）
     */
    private createConstellationLines(starMap: Map<number, any>): void {
        constellationLinesWithModels.forEach(constellation => {
            const positions: number[] = [];
            
            constellation.lines.forEach(([hip1, hip2]) => {
                const star1 = starMap.get(hip1);
                const star2 = starMap.get(hip2);
                
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
                
                // ⭐ Overlay 材质：透明、发光、不写深度
                const material = new THREE.LineBasicMaterial({
                    color: 0x4488ff,
                    transparent: true,
                    opacity: 0.5,
                    depthWrite: false,  // 关键！
                    depthTest: false     // 永远在最上层
                });
                
                const lines = new THREE.LineSegments(geometry, material);
                lines.renderOrder = 100;  // 确保在星点之上
                this.skyRootManager.overlayLayer.add(lines);
            }
        });
        
        console.log('✅ 星座连线已添加到 Overlay 层');
    }
    
    /**
     * 加载星座模型（Overlay 层）
     */
    private async loadConstellationModels(starMap: Map<number, any>): Promise<void> {
        const loadPromises = constellationModels.map(async (config) => {
            try {
                if (!config.centerHIP) return;
                
                const centerStar = starMap.get(config.centerHIP);
                if (!centerStar) return;
                
                const model = await ModelLoader.loadModel(config.modelPath);
                
                model.position.copy(centerStar.position);
                model.lookAt(0, this.camera.position.y, 0);  // Billboard 效果
                model.scale.setScalar(config.scale || 50);
                
                // ⭐ Overlay 材质：全息风格
                model.traverse((child: any) => {
                    if (child.isMesh) {
                        // 使用发光材质，不受光照影响
                        child.material = new THREE.MeshBasicMaterial({
                            color: 0x88ccff,
                            transparent: true,
                            opacity: 0.3,
                            depthWrite: false,  // 关键！
                            depthTest: false,
                            blending: THREE.AdditiveBlending
                        });
                    }
                });
                
                model.renderOrder = 50;  // 在星点之上，连线之下
                this.skyRootManager.overlayLayer.add(model);
                
                console.log(`  ✅ ${config.name}`);
                
            } catch (error) {
                console.error(`  ❌ ${config.name}:`, error);
            }
        });
        
        await Promise.all(loadPromises);
        console.log('🎉 星座模型已添加到 Overlay 层');
    }
    
    /**
     * 启用 AR 模式
     */
    public async enableARMode(): Promise<boolean> {
        if (typeof DeviceOrientationEvent === 'undefined') {
            return false;
        }
        
        const permission = await sensorManager.requestPermission();
        if (permission === 'denied') {
            return false;
        }
        
        sensorManager.addListener(this.handleSensorData);
        sensorManager.startListening();
        
        this.arMode = true;
        console.log('✅ AR 模式已启用');
        
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
        const orientation = sensorManager.getCameraOrientation(data);
        if (!orientation) return;
        
        this.telescopeCamera.updateFromDeviceSensor(
            orientation.azimuth,
            orientation.altitude
        );
    };
    
    /**
     * 主渲染循环
     */
    private animate = (): void => {
        const dt = 0.016;
        
        // ⭐ 核心：SkyRoot 跟随相机位置
        this.skyRootManager.update(this.camera.position);
        
        // 更新星场动画
        this.starfieldRenderer.update(dt);
        
        // 渲染
        this.renderer.render(this.scene, this.camera);
        
        // 渲染标签
        this.labelManager.render(this.skyRootManager.overlayLayer, this.camera);
        
        this.animationFrameId = requestAnimationFrame(this.animate);
    };
    
    /**
     * 获取统计信息
     */
    public getStats() {
        const starStats = this.starfieldRenderer.getStats();
        const orientation = this.telescopeCamera.getOrientation();
        
        return {
            ...starStats,
            observerLocation: this.observerLocation.name,
            zoom: this.telescopeCamera.getZoom(),
            azimuth: orientation.azimuth,
            altitude: orientation.altitude,
            arMode: this.arMode
        };
    }
    
    /**
     * 窗口大小调整
     */
    private onWindowResize = (): void => {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.starfieldRenderer.resize(window.innerWidth, window.innerHeight);
    };
    
    /**
     * 设置星座连线可见性
     */
    public setConstellationLinesVisible(visible: boolean): void {
        this.skyRootManager.overlayLayer.visible = visible;
    }
    
    /**
     * 清理
     */
    public dispose(): void {
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
        
        if (this.arMode) {
            this.disableARMode();
        }
        
        window.removeEventListener('resize', this.onWindowResize);
        
        this.starfieldRenderer.dispose();
        this.labelManager.dispose();
        this.renderer.dispose();
        this.container.removeChild(this.renderer.domElement);
    }
}
