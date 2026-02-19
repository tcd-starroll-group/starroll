import * as THREE from 'three';
import { PlanetConfig } from '../../types/planet';

/**
 * 探索模式场景渲染器
 * 用于近距离查看行星的详细信息
 */
export class ExploreSceneRenderer {
    public scene: THREE.Scene;
    private container: THREE.Group;
    private currentPlanet: THREE.Mesh | null = null;
    private planetData: PlanetConfig | null = null;
    
    // 光照
    private sunLight: THREE.DirectionalLight;
    private ambientLight: THREE.AmbientLight;
    private rimLight: THREE.DirectionalLight;
    
    constructor() {
        this.scene = new THREE.Scene();
        this.container = new THREE.Group();
        this.container.name = 'ExploreContainer';
        this.scene.add(this.container);
        
        // 设置光照
        this.setupLighting();
    }
    
    /**
     * 设置探索模式的光照
     */
    private setupLighting(): void {
        // 主光源（太阳光）
        this.sunLight = new THREE.DirectionalLight(0xffffff, 2.0);
        this.sunLight.position.set(5, 3, 5);
        this.sunLight.castShadow = true;
        this.scene.add(this.sunLight);
        
        // 环境光
        this.ambientLight = new THREE.AmbientLight(0x404040, 0.5);
        this.scene.add(this.ambientLight);
        
        // 边缘光（Rim Light）
        this.rimLight = new THREE.DirectionalLight(0x4488ff, 0.8);
        this.rimLight.position.set(-5, 0, -5);
        this.scene.add(this.rimLight);
    }
    
    /**
     * 加载并显示行星详细模型
     */
    public async loadPlanet(planetData: PlanetConfig): Promise<void> {
        // 清除当前行星
        if (this.currentPlanet) {
            this.container.remove(this.currentPlanet);
            this.currentPlanet.geometry.dispose();
            if (Array.isArray(this.currentPlanet.material)) {
                this.currentPlanet.material.forEach(m => m.dispose());
            } else {
                this.currentPlanet.material.dispose();
            }
        }
        
        this.planetData = planetData;
        
        // 创建高细节行星模型
        const geometry = new THREE.SphereGeometry(
            this.getExploreRadius(planetData),
            128, // 高精度
            128
        );
        
        const material = await this.createDetailedMaterial(planetData);
        
        this.currentPlanet = new THREE.Mesh(geometry, material);
        this.currentPlanet.castShadow = true;
        this.currentPlanet.receiveShadow = true;
        
        this.container.add(this.currentPlanet);
        
        console.log(`🔍 探索模式加载行星: ${planetData.name}`);
    }
    
    /**
     * 获取探索模式下的行星半径
     */
    private getExploreRadius(planetData: PlanetConfig): number {
        // 探索模式下使用更大的半径以显示细节
        const baseRadius = 50; // 基础半径
        const scale = Math.log(planetData.radius + 1) * 5;
        return baseRadius + scale;
    }
    
    /**
     * 创建详细材质（支持法线贴图、高光等）
     */
    private async createDetailedMaterial(planetData: PlanetConfig): Promise<THREE.Material> {
        // 基础颜色
        const color = new THREE.Color(planetData.color);
        
        // 创建 MeshStandardMaterial（支持 PBR）
        const material = new THREE.MeshStandardMaterial({
            color: color,
            metalness: 0.2,
            roughness: 0.8,
            emissive: color,
            emissiveIntensity: 0.1
        });
        
        // TODO: 如果有纹理贴图，可以在这里加载
        // const textureLoader = new THREE.TextureLoader();
        // material.map = await textureLoader.loadAsync(`/textures/${planetData.id}.jpg`);
        // material.normalMap = await textureLoader.loadAsync(`/textures/${planetData.id}_normal.jpg`);
        
        return material;
    }
    
    /**
     * 更新动画
     */
    public update(deltaTime: number): void {
        if (this.currentPlanet) {
            // 行星自转
            this.currentPlanet.rotation.y += deltaTime * 0.1;
        }
    }
    
    /**
     * 获取当前行星数据
     */
    public getCurrentPlanet(): PlanetConfig | null {
        return this.planetData;
    }
    
    /**
     * 清理资源
     */
    public dispose(): void {
        if (this.currentPlanet) {
            this.container.remove(this.currentPlanet);
            this.currentPlanet.geometry.dispose();
            if (Array.isArray(this.currentPlanet.material)) {
                this.currentPlanet.material.forEach(m => m.dispose());
            } else {
                this.currentPlanet.material.dispose();
            }
        }
    }
}
