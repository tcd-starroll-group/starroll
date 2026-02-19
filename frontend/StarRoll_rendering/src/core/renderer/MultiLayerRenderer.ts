import * as THREE from 'three';
import { SkyLayer } from './layers/SkyLayer';
import { DeepSpaceLayer } from './layers/DeepSpaceLayer';
import { PlanetSurfaceLayer } from './layers/PlanetSurfaceLayer';
import { PostProcessingManager } from './PostProcessingManager';
import { PlanetSystemRenderer } from './PlanetSystemRenderer';
import { CameraDirector } from './CameraDirector';
import { solarSystemData } from '../data/planets';
import { constellationLinesWithModels, constellationModels } from '../data/constellation-models';
import { loadStarCatalog } from '../../types/star-catalog';
import { PlanetConfig } from '../../types/planet';

export type ViewMode = 'overview' | 'explore';

/**
 * 多层渲染器 - StarWalk2 级别架构
 * 分层管理：Sky → Deep Space → Planet Surface → UI
 */
export class MultiLayerRenderer {
    // 核心渲染
    private renderer: THREE.WebGLRenderer;
    private camera: THREE.PerspectiveCamera;
    private container: HTMLElement;
    
    // 分层系统
    private skyLayer: SkyLayer;
    private deepSpaceLayer: DeepSpaceLayer;
    private planetSurfaceLayer: PlanetSurfaceLayer;
    private planetSystem: PlanetSystemRenderer;
    
    // 后处理
    private postProcessing: PostProcessingManager;
    
    // 相机控制
    public cameraDirector: CameraDirector;
    
    // 状态
    private currentMode: ViewMode = 'overview';
    private isTransitioning = false;
    private animationFrameId: number | null = null;
    
    // Floating Origin（浮动原点）
    private cameraWorldPosition: THREE.Vector3 = new THREE.Vector3();
    
    constructor(container: HTMLElement) {
        this.container = container;
        
        console.log('🎬 初始化多层渲染系统');
        console.log('架构: Sky Layer → Deep Space Layer → Planet Surface Layer');
        
        // 1. 初始化行星系统（提供基础渲染器和相机）
        this.planetSystem = new PlanetSystemRenderer(container);
        this.planetSystem.init(solarSystemData);
        this.planetSystem.setTimeScale(0.1);
        
        this.renderer = this.planetSystem.renderer;
        this.camera = this.planetSystem.camera;
        
        // 启用 HDR 和高质量渲染
        this.setupRendererQuality();
        
        // 2. 初始化相机控制
        this.cameraDirector = new CameraDirector(this.camera, container);
        
        // 3. 初始化各层
        this.skyLayer = new SkyLayer(this.planetSystem.scene);
        this.deepSpaceLayer = new DeepSpaceLayer(this.planetSystem.scene);
        this.planetSurfaceLayer = new PlanetSurfaceLayer();
        
        // 4. 初始化后处理
        this.postProcessing = new PostProcessingManager(
            this.renderer,
            this.planetSystem.scene,
            this.camera
        );
        
        // 5. 加载数据
        this.loadAllLayers();
        
        // 6. 启动渲染循环
        this.animate();
    }
    
    /**
     * 设置渲染器质量
     */
    private setupRendererQuality(): void {
        // HDR 渲染
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.0;
        
        // 高 DPI
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        // 抗锯齿
        this.renderer.antialias = true;
        
        // 阴影
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        // Logarithmic Depth Buffer（解决精度问题）
        this.renderer.logarithmicDepthBuffer = true;
        
        console.log('✅ 渲染器质量设置完成');
        console.log('   - HDR + ACES Tone Mapping');
        console.log('   - Logarithmic Depth Buffer');
        console.log('   - Pixel Ratio:', this.renderer.getPixelRatio());
    }
    
    /**
     * 加载所有层的数据
     */
    private async loadAllLayers(): Promise<void> {
        try {
            console.log('📂 加载所有层数据...');
            
            // 加载星表
            const stars = await loadStarCatalog();
            
            // Sky Layer: 真实星表
            await this.skyLayer.loadStarField(stars);
            this.skyLayer.createMilkyWay();
            
            // Deep Space Layer: 星座模型和连线
            await this.deepSpaceLayer.loadConstellations(
                stars,
                constellationLinesWithModels,
                constellationModels
            );
            
            console.log('✅ 所有层加载完成');
            
        } catch (error) {
            console.error('❌ 数据加载失败:', error);
        }
    }
    
    /**
     * 切换到探索模式
     */
    public async switchToExplore(planetData: PlanetConfig): Promise<void> {
        if (this.isTransitioning || this.currentMode === 'explore') return;
        
        console.log(`🔍 进入探索模式: ${planetData.name}`);
        
        this.isTransitioning = true;
        
        // 获取目标行星位置
        const targetPlanet = this.planetSystem.getPlanet(planetData.id);
        if (!targetPlanet) {
            console.error('未找到行星');
            this.isTransitioning = false;
            return;
        }
        
        const planetPosition = new THREE.Vector3();
        targetPlanet.mesh.getWorldPosition(planetPosition);
        
        // 计算相机目标位置
        const distance = 200;
        const direction = planetPosition.clone().normalize();
        const targetPosition = planetPosition.clone().add(direction.multiplyScalar(-distance));
        
        // 相机飞行动画
        await this.animateCameraTransition(targetPosition, planetPosition, 1.5);
        
        // 切换到探索场景
        this.currentMode = 'explore';
        
        // 加载高细节行星
        await this.planetSurfaceLayer.loadPlanet(planetData);
        
        // 调整曝光（行星近景通常需要降低曝光）
        this.postProcessing.setExposure(0.8);
        
        this.isTransitioning = false;
        console.log('✅ 探索模式已激活');
    }
    
    /**
     * 返回概览模式
     */
    public async switchToOverview(): Promise<void> {
        if (this.isTransitioning || this.currentMode === 'overview') return;
        
        console.log('🌍 返回概览模式');
        
        this.isTransitioning = true;
        
        // 目标位置（概览视角）
        const targetPosition = new THREE.Vector3(0, 300, 500);
        const targetTarget = new THREE.Vector3(0, 0, 0);
        
        await this.animateCameraTransition(targetPosition, targetTarget, 1.5);
        
        // 切换回概览场景
        this.currentMode = 'overview';
        
        // 恢复曝光
        this.postProcessing.setExposure(1.0);
        
        this.isTransitioning = false;
        console.log('✅ 概览模式已激活');
    }
    
    /**
     * 相机过渡动画
     */
    private animateCameraTransition(
        targetPosition: THREE.Vector3,
        targetLookAt: THREE.Vector3,
        duration: number
    ): Promise<void> {
        return new Promise((resolve) => {
            const startPosition = this.camera.position.clone();
            const startLookAt = this.cameraDirector['controls'].target.clone();
            const startTime = Date.now();
            
            const animate = () => {
                const elapsed = (Date.now() - startTime) / 1000;
                const progress = Math.min(elapsed / duration, 1);
                
                // 缓动
                const t = this.easeInOutCubic(progress);
                
                // 插值
                this.camera.position.lerpVectors(startPosition, targetPosition, t);
                this.cameraDirector['controls'].target.lerpVectors(startLookAt, targetLookAt, t);
                this.cameraDirector['controls'].update();
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    resolve();
                }
            };
            
            animate();
        });
    }
    
    /**
     * 缓动函数
     */
    private easeInOutCubic(t: number): number {
        return t < 0.5 
            ? 4 * t * t * t 
            : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }
    
    /**
     * 主渲染循环
     */
    private animate = () => {
        const dt = 0.016;
        
        // 更新 Floating Origin（天穹层跟随相机）
        this.cameraWorldPosition.copy(this.camera.position);
        
        // 更新相机控制
        this.cameraDirector.update(dt);
        
        if (this.currentMode === 'overview') {
            // Overview 模式：渲染所有层
            
            // 1. Sky Layer（跟随相机位置）
            this.skyLayer.update(this.cameraWorldPosition, dt);
            
            // 2. Deep Space Layer（星座模型）
            this.deepSpaceLayer.update(dt);
            
            // 3. Planet System（太阳系）
            this.planetSystem.update(dt);
            
        } else {
            // Explore 模式：只渲染 Sky + Planet Surface
            
            // Sky Layer 仍然可见（星空背景）
            this.skyLayer.update(this.cameraWorldPosition, dt);
            
            // Planet Surface Layer
            this.planetSurfaceLayer.update(dt);
        }
        
        // 更新后处理
        this.postProcessing.update(dt);
        
        // 渲染（使用后处理）
        if (this.currentMode === 'overview') {
            this.postProcessing.render();
        } else {
            // Explore 模式：渲染行星表面场景
            this.renderer.render(this.planetSurfaceLayer.scene, this.camera);
        }
        
        this.animationFrameId = requestAnimationFrame(this.animate);
    };
    
    /**
     * 设置星座可见性
     */
    public setConstellationsVisible(visible: boolean): void {
        const renderer = this.deepSpaceLayer.getConstellationRenderer();
        renderer.setConstellationModelsVisible(visible);
        renderer.setConstellationLinesVisible(visible);
    }
    
    /**
     * 获取统计信息
     */
    public getStats() {
        return this.deepSpaceLayer.getConstellationRenderer().getStats();
    }
    
    /**
     * 获取行星系统
     */
    public getPlanetSystem(): PlanetSystemRenderer {
        return this.planetSystem;
    }
    
    /**
     * 窗口大小调整
     */
    public resize(): void {
        this.planetSystem.onResize();
        this.postProcessing.resize(window.innerWidth, window.innerHeight);
    }
    
    /**
     * 清理
     */
    public dispose(): void {
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
        this.skyLayer.dispose();
        this.deepSpaceLayer.dispose();
        this.planetSurfaceLayer.dispose();
        this.postProcessing.dispose();
        this.planetSystem.dispose();
    }
}
