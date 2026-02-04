import * as THREE from 'three';
import { PlanetSystemRenderer } from './PlanetSystemRenderer';
import { ExploreSceneRenderer } from './ExploreSceneRenderer';
import { StarCatalogRendererWithModels } from './StarCatalogRendererWithModels';
import { CameraDirector } from './CameraDirector';
import { GalaxyBackgroundRenderer } from './GalaxyBackgroundRenderer';
import { solarSystemData } from '../data/planets';
import { constellationLinesWithModels, constellationModels } from '../data/constellation-models';
import { loadStarCatalog } from '../../types/star-catalog';
import { PlanetConfig } from '../../types/planet';

export type SceneMode = 'overview' | 'explore';
export type ViewTarget = 'system' | 'starry';

/**
 * 双场景渲染器
 * 管理 Overview（概览）和 Explore（探索）两个场景
 */
export class DualSceneRenderer {
    // 渲染器和相机
    private renderer: THREE.WebGLRenderer;
    private camera: THREE.PerspectiveCamera;
    private domElement: HTMLElement;
    
    // Overview 场景（概览模式）
    private overviewScene: THREE.Scene;
    private planetSystem: PlanetSystemRenderer;
    private starCatalogRenderer: StarCatalogRendererWithModels;
    private galaxyRenderer: GalaxyBackgroundRenderer;
    
    // Explore 场景（探索模式）
    private exploreRenderer: ExploreSceneRenderer;
    
    // 相机控制
    public cameraDirector: CameraDirector;
    
    // 状态
    private currentMode: SceneMode = 'overview';
    private currentTarget: ViewTarget = 'system';
    private isTransitioning = false;
    private animationFrameId: number | null = null;
    
    // 过渡参数
    private transitionProgress = 0;
    private transitionDuration = 1.5; // 秒
    
    constructor(container: HTMLElement) {
        this.domElement = container;
        
        // 初始化 Overview 场景
        this.planetSystem = new PlanetSystemRenderer(container);
        this.planetSystem.init(solarSystemData);
        this.planetSystem.setTimeScale(0.1);
        
        this.overviewScene = this.planetSystem.scene;
        this.renderer = this.planetSystem.renderer;
        this.camera = this.planetSystem.camera;
        
        // 初始化相机控制
        this.cameraDirector = new CameraDirector(this.camera, container);
        
        // 初始化星空背景
        this.galaxyRenderer = new GalaxyBackgroundRenderer(this.overviewScene);
        
        // 初始化星表渲染器
        this.starCatalogRenderer = new StarCatalogRendererWithModels(this.overviewScene);
        
        // 初始化 Explore 场景
        this.exploreRenderer = new ExploreSceneRenderer();
        
        // 加载星表数据
        this.loadStarCatalogData();
        
        // 设置光照
        this.setupOverviewLighting();
        
        // 启动渲染循环
        this.animate();
        
        console.log('🎬 双场景渲染器初始化完成');
    }
    
    /**
     * 设置 Overview 场景光照
     */
    private setupOverviewLighting(): void {
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
        this.overviewScene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight.position.set(1, 1, 1);
        this.overviewScene.add(directionalLight);
    }
    
    /**
     * 加载星表数据
     */
    private async loadStarCatalogData(): Promise<void> {
        try {
            console.log('🌟 加载星表数据...');
            const stars = await loadStarCatalog();
            await this.starCatalogRenderer.loadStarCatalog(
                stars,
                constellationLinesWithModels,
                constellationModels
            );
            console.log('✅ 星表加载完成');
        } catch (error) {
            console.error('❌ 星表加载失败:', error);
        }
    }
    
    /**
     * 切换场景模式
     */
    public async switchToExplore(planetData: PlanetConfig): Promise<void> {
        if (this.isTransitioning || this.currentMode === 'explore') return;
        
        console.log(`🚀 切换到探索模式: ${planetData.name}`);
        
        this.isTransitioning = true;
        this.transitionProgress = 0;
        
        // 获取目标行星位置
        const targetPlanet = this.planetSystem.getPlanet(planetData.id);
        if (!targetPlanet) {
            console.error('未找到行星:', planetData.id);
            this.isTransitioning = false;
            return;
        }
        
        // 保存相机初始位置
        const startPosition = this.camera.position.clone();
        const startTarget = this.cameraDirector['controls'].target.clone();
        
        // 计算目标位置（距离行星一定距离）
        const planetPosition = new THREE.Vector3();
        targetPlanet.mesh.getWorldPosition(planetPosition);
        
        const distance = 150;
        const direction = planetPosition.clone().normalize();
        const targetPosition = planetPosition.clone().add(direction.multiplyScalar(-distance));
        
        // 开始过渡动画
        const startTime = Date.now();
        
        const transitionLoop = () => {
            const elapsed = (Date.now() - startTime) / 1000;
            this.transitionProgress = Math.min(elapsed / this.transitionDuration, 1);
            
            // 使用 easeInOutCubic 缓动
            const t = this.easeInOutCubic(this.transitionProgress);
            
            // 相机位置插值
            this.camera.position.lerpVectors(startPosition, targetPosition, t);
            this.cameraDirector['controls'].target.lerpVectors(startTarget, planetPosition, t);
            this.cameraDirector['controls'].update();
            
            if (this.transitionProgress < 1) {
                requestAnimationFrame(transitionLoop);
            } else {
                // 过渡完成，切换场景
                this.finishTransitionToExplore(planetData);
            }
        };
        
        transitionLoop();
    }
    
    /**
     * 完成切换到探索模式
     */
    private async finishTransitionToExplore(planetData: PlanetConfig): Promise<void> {
        this.currentMode = 'explore';
        
        // 加载探索场景
        await this.exploreRenderer.loadPlanet(planetData);
        
        this.isTransitioning = false;
        console.log('✅ 探索模式已激活');
    }
    
    /**
     * 切换回概览模式
     */
    public async switchToOverview(): Promise<void> {
        if (this.isTransitioning || this.currentMode === 'overview') return;
        
        console.log('🌍 切换回概览模式');
        
        this.isTransitioning = true;
        this.transitionProgress = 0;
        
        // 保存当前位置
        const startPosition = this.camera.position.clone();
        const startTarget = this.cameraDirector['controls'].target.clone();
        
        // 目标位置（概览视角）
        const targetPosition = new THREE.Vector3(0, 200, 300);
        const targetTarget = new THREE.Vector3(0, 0, 0);
        
        const startTime = Date.now();
        
        const transitionLoop = () => {
            const elapsed = (Date.now() - startTime) / 1000;
            this.transitionProgress = Math.min(elapsed / this.transitionDuration, 1);
            
            const t = this.easeInOutCubic(this.transitionProgress);
            
            this.camera.position.lerpVectors(startPosition, targetPosition, t);
            this.cameraDirector['controls'].target.lerpVectors(startTarget, targetTarget, t);
            this.cameraDirector['controls'].update();
            
            if (this.transitionProgress < 1) {
                requestAnimationFrame(transitionLoop);
            } else {
                this.finishTransitionToOverview();
            }
        };
        
        transitionLoop();
    }
    
    /**
     * 完成切换回概览模式
     */
    private finishTransitionToOverview(): void {
        this.currentMode = 'overview';
        this.exploreRenderer.dispose();
        this.isTransitioning = false;
        console.log('✅ 概览模式已激活');
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
     * 渲染循环
     */
    private animate = () => {
        const dt = 0.016;
        
        // 更新相机控制
        this.cameraDirector.update(dt);
        
        // 根据当前模式渲染不同场景
        if (this.currentMode === 'overview') {
            // 概览模式：渲染行星系统和星空
            this.planetSystem.update(dt);
            this.galaxyRenderer.update(dt);
            this.starCatalogRenderer.update(dt);
            this.renderer.render(this.overviewScene, this.camera);
        } else {
            // 探索模式：渲染详细行星场景
            this.exploreRenderer.update(dt);
            this.renderer.render(this.exploreRenderer.scene, this.camera);
        }
        
        this.animationFrameId = requestAnimationFrame(this.animate);
    }
    
    /**
     * 设置视图目标
     */
    public setViewTarget(target: ViewTarget): void {
        this.currentTarget = target;
        if (target === 'system') {
            this.starCatalogRenderer.setConstellationLinesVisible(false);
            this.starCatalogRenderer.setConstellationModelsVisible(false);
        } else {
            this.starCatalogRenderer.setConstellationLinesVisible(true);
            this.starCatalogRenderer.setConstellationModelsVisible(true);
        }
    }
    
    /**
     * 获取当前模式
     */
    public getCurrentMode(): SceneMode {
        return this.currentMode;
    }
    
    /**
     * 获取行星系统
     */
    public getPlanetSystem(): PlanetSystemRenderer {
        return this.planetSystem;
    }
    
    /**
     * 获取星表渲染器
     */
    public getStarCatalogRenderer(): StarCatalogRendererWithModels {
        return this.starCatalogRenderer;
    }
    
    /**
     * 窗口大小调整
     */
    public resize(): void {
        this.planetSystem.onResize();
    }
    
    /**
     * 清理资源
     */
    public dispose(): void {
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
        this.planetSystem.dispose();
        this.starCatalogRenderer.dispose();
        this.exploreRenderer.dispose();
    }
}
