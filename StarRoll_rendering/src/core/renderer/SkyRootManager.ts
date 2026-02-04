import * as THREE from 'three';

/**
 * SkyRoot 管理器
 * 管理 Sky Layer，永远跟随相机位置（但不产生视差）
 */
export class SkyRootManager {
    public skyRoot: THREE.Group;
    
    // 子层
    public skyDomeLayer: THREE.Group;      // 银河/星云背景
    public starfieldLayer: THREE.Group;    // 星点
    public overlayLayer: THREE.Group;      // 星座模型/连线/标签
    
    constructor() {
        this.skyRoot = new THREE.Group();
        this.skyRoot.name = 'SkyRoot';
        
        // 创建子层
        this.skyDomeLayer = new THREE.Group();
        this.skyDomeLayer.name = 'SkyDome';
        
        this.starfieldLayer = new THREE.Group();
        this.starfieldLayer.name = 'Starfield';
        
        this.overlayLayer = new THREE.Group();
        this.overlayLayer.name = 'Overlay';
        this.overlayLayer.renderOrder = 999;  // 最后渲染，永远在上层
        
        // 添加到 SkyRoot
        this.skyRoot.add(this.skyDomeLayer);
        this.skyRoot.add(this.starfieldLayer);
        this.skyRoot.add(this.overlayLayer);
    }
    
    /**
     * 更新 SkyRoot 位置（跟随相机）
     */
    public update(cameraPosition: THREE.Vector3): void {
        // ⭐ 核心：SkyRoot 永远跟随相机位置
        // 这样星空永远在"无限远"，不会产生视差
        this.skyRoot.position.copy(cameraPosition);
    }
    
    /**
     * 添加到场景
     */
    public addToScene(scene: THREE.Scene): void {
        scene.add(this.skyRoot);
    }
    
    /**
     * 从场景移除
     */
    public removeFromScene(scene: THREE.Scene): void {
        scene.remove(this.skyRoot);
    }
}
