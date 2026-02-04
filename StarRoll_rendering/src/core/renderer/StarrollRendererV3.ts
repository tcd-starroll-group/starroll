import * as THREE from 'three';
import { PlanetSystemRenderer } from './PlanetSystemRenderer';
import { CameraDirector } from './CameraDirector';
import { GalaxyBackgroundRenderer } from './GalaxyBackgroundRenderer';
import { StarCatalogRendererWithModels } from './StarCatalogRendererWithModels';
import { solarSystemData } from '../data/planets';
import { constellationLinesWithModels, constellationModels } from '../data/constellation-models';
import { loadStarCatalog } from '../../types/star-catalog';

export type ViewMode = 'system' | 'starry';

export interface ConstellationInfo {
    id: string;
    name: string;
    position: THREE.Vector3;
}

/**
 * StarRoll 渲染器 V3
 * 支持真实星表 + 星座 3D 模型
 */
export class StarrollRendererV3 {
    private scene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private renderer: THREE.WebGLRenderer;
    private domElement: HTMLElement;
    private animationFrameId: number | null = null;
    
    // 子系统
    public planets: PlanetSystemRenderer; 
    public starCatalogRenderer: StarCatalogRendererWithModels;
    public galaxyRenderer: GalaxyBackgroundRenderer;
    
    // 相机导演
    public cameraDirector: CameraDirector;
    
    // 加载状态
    private isStarCatalogLoaded = false;
    
    constructor(container: HTMLElement) {
        this.domElement = container;
        
        // 1. 初始化行星系统
        this.planets = new PlanetSystemRenderer(container);
        this.planets.init(solarSystemData);
        this.planets.setTimeScale(0.1); 

        // 2. 初始化相机导演
        this.cameraDirector = new CameraDirector(this.planets.camera, container);
        
        // 3. 初始化星空背景
        this.galaxyRenderer = new GalaxyBackgroundRenderer(this.planets.scene);

        // 4. 初始化增强版星表渲染器（支持 3D 模型）
        this.starCatalogRenderer = new StarCatalogRendererWithModels(this.planets.scene);
        
        // 获取引用
        this.scene = this.planets.scene;
        this.camera = this.planets.camera;
        this.renderer = this.planets.renderer;
        
        // 添加光照以显示模型纹理
        this.setupLighting();
        
        // 5. 异步加载星表和模型
        this.loadStarCatalogData();
        
        // 6. 启动循环
        this.animate();
    }

    /**
     * 设置场景光照
     */
    private setupLighting(): void {
        // 环境光 - 提供基础照明
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);
        
        // 平行光 - 模拟阳光
        const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight1.position.set(1, 1, 1);
        this.scene.add(directionalLight1);
        
        const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
        directionalLight2.position.set(-1, -1, -1);
        this.scene.add(directionalLight2);
        
        console.log('💡 场景光照已设置');
    }
    
    /**
     * 加载星表数据和 3D 模型
     */
    private async loadStarCatalogData(): Promise<void> {
        try {
            console.log('🌟 StarRoll V3 - 加载真实星表 + 3D 模型');
            console.log('📂 加载星表数据...');
            const stars = await loadStarCatalog();
            
            console.log('🎨 加载星座连线和 3D 模型...');
            await this.starCatalogRenderer.loadStarCatalog(
                stars,
                constellationLinesWithModels,
                constellationModels
            );
            
            this.isStarCatalogLoaded = true;
            
            // 打印统计信息
            const stats = this.starCatalogRenderer.getStats();
            console.log('📊 渲染统计:', stats);
            console.log(`✅ 系统加载完成！`);
            console.log(`   - 恒星: ${stats.visibleStars}/${stats.totalStars} 颗`);
            console.log(`   - 星座连线: ${stats.constellations} 个`);
            console.log(`   - 3D 模型: ${stats.models} 个`);
            
        } catch (error) {
            console.error('❌ 加载失败:', error);
        }
    }

    private animate = () => {
        const dt = 0.016; 
        
        // 更新控制器
        this.cameraDirector.update(dt);

        // 更新行星
        this.planets.update(dt);
        
        // 更新背景
        this.galaxyRenderer.update(dt);
        
        // 更新星空和模型
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
            // 行星模式：隐藏星座
            this.starCatalogRenderer.setConstellationLinesVisible(false);
            this.starCatalogRenderer.setConstellationModelsVisible(false);
        } else {
            // 星空模式：显示星座
            this.starCatalogRenderer.setConstellationLinesVisible(true);
            this.starCatalogRenderer.setConstellationModelsVisible(true);
        }
    }
    
    /**
     * 设置星座连线可见性
     */
    public setConstellationLinesVisible(visible: boolean): void {
        this.starCatalogRenderer.setConstellationLinesVisible(visible);
    }
    
    /**
     * 设置星座模型可见性
     */
    public setConstellationModelsVisible(visible: boolean): void {
        this.starCatalogRenderer.setConstellationModelsVisible(visible);
    }
    
    /**
     * 显示/隐藏特定星座
     */
    public setConstellationVisible(id: string, visible: boolean): void {
        this.starCatalogRenderer.setConstellationVisible(id, visible);
    }
    
    /**
     * 获取统计信息
     */
    public getStats() {
        return this.starCatalogRenderer.getStats();
    }
    
    /**
     * 聚焦到指定星座
     */
    public focusConstellation(id: string): void {
        const model = this.starCatalogRenderer['constellationModels'].children.find((m: any) => m.name === id);
        if (model) {
            const targetPos = model.userData.centerPosition as THREE.Vector3;
            if (targetPos) {
                // 计算相机位置（距离星座一定距离）
                const distance = 150;
                const direction = targetPos.clone().normalize();
                const cameraPos = targetPos.clone().add(direction.multiplyScalar(-distance));
                
                // 平滑移动相机
                this.cameraDirector.focusPosition(targetPos, distance);
                
                console.log(`🎯 聚焦到星座: ${model.userData.constellationName}`);
            }
        } else {
            console.warn(`未找到星座: ${id}`);
        }
    }
    
    /**
     * 获取所有星座信息
     */
    public getConstellations(): ConstellationInfo[] {
        return this.starCatalogRenderer['constellationModels'].children.map((model: any) => ({
            id: model.name,
            name: model.userData.constellationName,
            position: model.userData.centerPosition
        }));
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
