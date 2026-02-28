import * as THREE from 'three';
import { StarCatalogRendererWithModels } from '../StarCatalogRendererWithModels';
import type { StarMeta, ConstellationLines } from '../../../types/star-meta';
import type { ConstellationModel } from '../../data/constellation-models';

/**
 * Deep Space Layer（深空层）
 * 太阳系概览、星座模型、星座连线
 */
export class DeepSpaceLayer {
    private scene: THREE.Scene;
    private container: THREE.Group;
    private constellationRenderer: StarCatalogRendererWithModels;
    
    // 中尺度空间原点（太阳系中心）
    private origin: THREE.Vector3 = new THREE.Vector3(0, 0, 0);
    
    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.container = new THREE.Group();
        this.container.name = 'DeepSpaceLayer';
        this.scene.add(this.container);
        
        // 初始化星座渲染器
        this.constellationRenderer = new StarCatalogRendererWithModels(scene);
    }
    
    /**
     * 加载星座模型和连线
     */
    public async loadConstellations(
        stars: StarMeta[],
        lines: ConstellationLines[],
        models: ConstellationModel[]
    ): Promise<void> {
        await this.constellationRenderer.loadStarCatalog(stars, lines, models);
    }
    
    /**
     * 更新（中尺度空间，坐标相对稳定）
     */
    public update(deltaTime: number): void {
        this.constellationRenderer.update(deltaTime);
    }
    
    /**
     * 设置可见性
     */
    public setVisible(visible: boolean): void {
        this.container.visible = visible;
    }
    
    /**
     * 获取星座渲染器
     */
    public getConstellationRenderer(): StarCatalogRendererWithModels {
        return this.constellationRenderer;
    }
    
    /**
     * 清理
     */
    public dispose(): void {
        this.constellationRenderer.dispose();
        this.scene.remove(this.container);
    }
}
