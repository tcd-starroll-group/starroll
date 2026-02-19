import * as THREE from 'three';
import { PlanetSystemRenderer } from './PlanetSystemRenderer';
import { ConstellationRenderer } from './ConstellationRenderer';
import { CameraDirector } from './CameraDirector';
import { GalaxyBackgroundRenderer } from './GalaxyBackgroundRenderer';
import { solarSystemData } from '../data/planets';
import { sampleConstellations } from '../data/constellations';
import { PlanetConfig } from '../../types/planet';
import { ConstellationData } from '../../types/constellation';
import { AstroCoordinates } from '../astronomy/Coordinates';

export type ViewMode = 'system' | 'starry'; // 太阳系模式 | 星空模式

export class StarrollRenderer {
    private scene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private renderer: THREE.WebGLRenderer;
    private domElement: HTMLElement;
    private animationFrameId: number | null = null;
    
    // 子系统
    public planets: PlanetSystemRenderer; 
    public constellationRenderer: ConstellationRenderer;
    public galaxyRenderer: GalaxyBackgroundRenderer;
    
    // 相机导演
    public cameraDirector: CameraDirector;
    
    constructor(container: HTMLElement) {
        this.domElement = container;
        
        // 1. 初始化行星系统 (作为主系统)
        this.planets = new PlanetSystemRenderer(container);
        this.planets.init(solarSystemData);
        // 【修改】降低默认速度
        this.planets.setTimeScale(0.1); 

        // 2. 初始化相机导演 (接管 PlanetSystemRenderer 创建的 camera)
        this.cameraDirector = new CameraDirector(this.planets.camera, container);
        
        // 3. 初始化高级星空背景
        this.galaxyRenderer = new GalaxyBackgroundRenderer(this.planets.scene);

        // 4. 初始化星座系统 (共享行星系统的 scene)
        this.constellationRenderer = new ConstellationRenderer(this.planets.scene);
        // 异步加载星座（包含可能的外部GLTF模型）
        this.constellationRenderer.loadConstellations(sampleConstellations).catch(error => {
            console.error('Failed to load constellations:', error);
        });
        
        // 5. 启动循环
        this.animate();
    }

    private animate = () => {
        const dt = 0.016; 
        
        // 更新控制器
        this.cameraDirector.update(dt);

        // 更新行星
        this.planets.update(dt);
        
        // 更新背景 (星云流动、星星闪烁)
        this.galaxyRenderer.update(dt);
        
        // 更新星座 (呼吸、自转)
        this.constellationRenderer.update(dt);
        
        this.animationFrameId = requestAnimationFrame(this.animate);
    }
    
    public focus(target: PlanetConfig | ConstellationData | null) {
        if (!target) {
            this.cameraDirector.resetView();
            return;
        }

        // 判断是行星还是星座
        if ((target as any).orbitRadius !== undefined) {
            // 是行星
            const planetData = this.planets.getPlanet(target.id);
            if (planetData) {
                this.cameraDirector.focus(planetData.mesh);
            }
        } else {
            // 是星座
            const c = target as ConstellationData;
            // 计算星座中心的世界坐标
            const center = AstroCoordinates.raDecToVector3(c.center.ra, c.center.dec, 450);
            // 聚焦到该坐标，保持 100 距离
            this.cameraDirector.focusPosition(center, 100);
        }
    }
    
    
    public setMode(mode: ViewMode) {
        if (mode === 'system') {
            // 行星模式：隐藏星座线和模型，保留星点背景
            this.constellationRenderer.setVisibleMode('none'); 
        } else {
            // 星空模式
            this.constellationRenderer.setVisibleMode('all');
        }
    }
    
    public resize() {
        this.planets.onResize();
    }
    
    public dispose() {
        if (this.animationFrameId) cancelAnimationFrame(this.animationFrameId);
        this.planets.dispose();
    }
}

