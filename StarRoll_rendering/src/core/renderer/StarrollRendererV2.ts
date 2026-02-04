import * as THREE from 'three';
import { PlanetSystemRenderer } from './PlanetSystemRenderer';
import { CameraDirector } from './CameraDirector';
import { GalaxyBackgroundRenderer } from './GalaxyBackgroundRenderer';
import { StarCatalogRenderer } from './StarCatalogRenderer';
import { solarSystemData } from '../data/planets';
import { constellationLinesData } from '../data/constellation-lines';
import { loadStarCatalog } from '../../types/star-catalog';

export type ViewMode = 'system' | 'starry'; // 太阳系模式 | 星空模式

/**
 * StarRoll 渲染器 V2
 * 集成真实星表数据渲染
 */
export class StarrollRendererV2 {
    private scene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private renderer: THREE.WebGLRenderer;
    private domElement: HTMLElement;
    private animationFrameId: number | null = null;
    
    // 子系统
    public planets: PlanetSystemRenderer; 
    public starCatalogRenderer: StarCatalogRenderer;
    public galaxyRenderer: GalaxyBackgroundRenderer;
    
    // 相机导演
    public cameraDirector: CameraDirector;
    
    // 加载状态
    private isStarCatalogLoaded = false;
    
    constructor(container: HTMLElement) {
        this.domElement = container;
        
        // 1. 初始化行星系统 (作为主系统)
        this.planets = new PlanetSystemRenderer(container);
        this.planets.init(solarSystemData);
        // 降低默认速度
        this.planets.setTimeScale(0.1); 

        // 2. 初始化相机导演
        this.cameraDirector = new CameraDirector(this.planets.camera, container);
        
        // 3. 初始化高级星空背景
        this.galaxyRenderer = new GalaxyBackgroundRenderer(this.planets.scene);

        // 4. 初始化真实星表渲染器
        this.starCatalogRenderer = new StarCatalogRenderer(this.planets.scene);
        
        // 获取引用
        this.scene = this.planets.scene;
        this.camera = this.planets.camera;
        this.renderer = this.planets.renderer;
        
        // 5. 异步加载星表数据
        this.loadStarCatalogData();
        
        // 6. 启动循环
        this.animate();
    }

    /**
     * 加载星表数据
     */
    private async loadStarCatalogData(): Promise<void> {
        try {
            console.log('Loading star catalog...');
            const stars = await loadStarCatalog();
            
            // 加载星表和星座连线
            await this.starCatalogRenderer.loadStarCatalog(stars, constellationLinesData);
            
            this.isStarCatalogLoaded = true;
            
            // 打印统计信息
            const stats = this.starCatalogRenderer.getStats();
            console.log('Star Catalog Stats:', stats);
            
        } catch (error) {
            console.error('Failed to load star catalog:', error);
        }
    }

    private animate = () => {
        const dt = 0.016; 
        
        // 更新控制器
        this.cameraDirector.update(dt);

        // 更新行星
        this.planets.update(dt);
        
        // 更新背景 (星云流动)
        this.galaxyRenderer.update(dt);
        
        // 更新星空 (星星闪烁)
        if (this.isStarCatalogLoaded) {
            this.starCatalogRenderer.update(dt);
        }
        
        this.animationFrameId = requestAnimationFrame(this.animate);
    }
    
    /**
     * 设置显示模式
     */
    public setMode(mode: ViewMode): void {
        if (mode === 'system') {
            // 行星模式：隐藏星座连线
            this.starCatalogRenderer.setConstellationLinesVisible(false);
        } else {
            // 星空模式：显示星座连线
            this.starCatalogRenderer.setConstellationLinesVisible(true);
        }
    }
    
    /**
     * 设置星座连线可见性
     */
    public setConstellationLinesVisible(visible: boolean): void {
        this.starCatalogRenderer.setConstellationLinesVisible(visible);
    }
    
    /**
     * 显示/隐藏特定星座
     */
    public setConstellationVisible(id: string, visible: boolean): void {
        this.starCatalogRenderer.setConstellationVisible(id, visible);
    }
    
    /**
     * 获取星表统计信息
     */
    public getStarCatalogStats() {
        return this.starCatalogRenderer.getStats();
    }
    
    public resize(): void {
        this.planets.onResize();
    }
    
    public dispose(): void {
        if (this.animationFrameId) cancelAnimationFrame(this.animationFrameId);
        this.starCatalogRenderer.dispose();
        this.planets.dispose();
    }
}
