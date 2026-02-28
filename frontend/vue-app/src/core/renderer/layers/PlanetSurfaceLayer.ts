import * as THREE from 'three';
import { PlanetConfig } from '../../../types/planet';

/**
 * Planet Surface Layer（近景层）
 * 行星高细节模型 - 地形、云层、大气
 */
export class PlanetSurfaceLayer {
    public scene: THREE.Scene;
    private container: THREE.Group;
    private currentPlanet: THREE.Group | null = null;
    private planetData: PlanetConfig | null = null;
    
    // 高细节渲染
    private planetMesh: THREE.Mesh | null = null;
    private atmosphereMesh: THREE.Mesh | null = null;
    private cloudsMesh: THREE.Mesh | null = null;
    
    // 光照
    private sunLight: THREE.DirectionalLight;
    private fillLight: THREE.DirectionalLight;
    private ambientLight: THREE.AmbientLight;
    
    constructor() {
        this.scene = new THREE.Scene();
        this.container = new THREE.Group();
        this.container.name = 'PlanetSurfaceLayer';
        this.scene.add(this.container);
        
        // 设置专业光照
        this.setupLighting();
    }
    
    /**
     * 设置光照系统
     */
    private setupLighting(): void {
        // 主光源（太阳）- 高强度
        this.sunLight = new THREE.DirectionalLight(0xffffff, 3.0);
        this.sunLight.position.set(100, 50, 100);
        this.sunLight.castShadow = true;
        this.sunLight.shadow.mapSize.width = 2048;
        this.sunLight.shadow.mapSize.height = 2048;
        this.scene.add(this.sunLight);
        
        // 补光（模拟星光反射）
        this.fillLight = new THREE.DirectionalLight(0x4466aa, 0.5);
        this.fillLight.position.set(-100, -50, -100);
        this.scene.add(this.fillLight);
        
        // 环境光（防止阴影过黑）
        this.ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(this.ambientLight);
    }
    
    /**
     * 加载行星高细节模型
     */
    public async loadPlanet(planetData: PlanetConfig): Promise<void> {
        console.log(`🔍 Surface Layer: 加载行星 ${planetData.name}`);
        
        // 清除旧模型
        this.clearPlanet();
        
        this.planetData = planetData;
        this.currentPlanet = new THREE.Group();
        
        // 计算行星半径（探索模式下放大）
        const radius = this.calculatePlanetRadius(planetData);
        
        // 1. 创建主行星体
        this.planetMesh = this.createPlanetMesh(planetData, radius);
        this.currentPlanet.add(this.planetMesh);
        
        // 2. 创建大气层（如果有）
        if (this.hasMajorAtmosphere(planetData)) {
            this.atmosphereMesh = this.createAtmosphere(radius);
            this.currentPlanet.add(this.atmosphereMesh);
        }
        
        // 3. 创建云层（如果是地球）
        if (planetData.id === 'EAR') {
            this.cloudsMesh = this.createClouds(radius);
            this.currentPlanet.add(this.cloudsMesh);
        }
        
        this.container.add(this.currentPlanet);
        console.log(`✅ 行星加载完成，半径: ${radius.toFixed(1)}`);
    }
    
    /**
     * 计算探索模式下的行星半径
     */
    private calculatePlanetRadius(planetData: PlanetConfig): number {
        // 基础半径 + 对数缩放
        const baseRadius = 80;
        const logScale = Math.log10(planetData.radius + 1) * 15;
        return baseRadius + logScale;
    }
    
    /**
     * 创建行星主体
     */
    private createPlanetMesh(planetData: PlanetConfig, radius: number): THREE.Mesh {
        const geometry = new THREE.SphereGeometry(radius, 128, 128);
        
        // 高质量 PBR 材质
        const material = new THREE.MeshStandardMaterial({
            color: new THREE.Color(planetData.color),
            metalness: 0.1,
            roughness: 0.7,
            emissive: new THREE.Color(planetData.color),
            emissiveIntensity: 0.05
        });
        
        // TODO: 加载真实纹理贴图
        // const textureLoader = new THREE.TextureLoader();
        // material.map = await textureLoader.loadAsync(`/textures/planets/${planetData.id}_color.jpg`);
        // material.normalMap = await textureLoader.loadAsync(`/textures/planets/${planetData.id}_normal.jpg`);
        // material.roughnessMap = await textureLoader.loadAsync(`/textures/planets/${planetData.id}_roughness.jpg`);
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        
        return mesh;
    }
    
    /**
     * 创建大气层
     */
    private createAtmosphere(planetRadius: number): THREE.Mesh {
        const geometry = new THREE.SphereGeometry(planetRadius * 1.05, 64, 64);
        
        const material = new THREE.ShaderMaterial({
            uniforms: {
                uColor: { value: new THREE.Color(0x4488ff) },
                uSunDirection: { value: new THREE.Vector3(1, 0.5, 1).normalize() }
            },
            vertexShader: `
                varying vec3 vNormal;
                varying vec3 vPosition;
                
                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    vPosition = position;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform vec3 uColor;
                uniform vec3 uSunDirection;
                varying vec3 vNormal;
                varying vec3 vPosition;
                
                void main() {
                    vec3 normal = normalize(vNormal);
                    vec3 viewDir = normalize(cameraPosition - vPosition);
                    
                    // 大气散射效果
                    float rim = 1.0 - abs(dot(viewDir, normal));
                    float scattering = pow(rim, 3.0);
                    
                    // 日侧亮，夜侧暗
                    float sunDot = max(0.0, dot(normal, uSunDirection));
                    float daylight = pow(sunDot, 0.5);
                    
                    vec3 atmosphereColor = uColor * (daylight * 0.5 + 0.3);
                    float alpha = scattering * 0.6;
                    
                    gl_FragColor = vec4(atmosphereColor, alpha);
                }
            `,
            transparent: true,
            side: THREE.BackSide,
            depthWrite: false,
            blending: THREE.AdditiveBlending
        });
        
        return new THREE.Mesh(geometry, material);
    }
    
    /**
     * 创建云层（地球）
     */
    private createClouds(planetRadius: number): THREE.Mesh {
        const geometry = new THREE.SphereGeometry(planetRadius * 1.01, 64, 64);
        
        const material = new THREE.MeshStandardMaterial({
            color: 0xffffff,
            transparent: true,
            opacity: 0.4,
            metalness: 0,
            roughness: 1.0
        });
        
        // TODO: 加载云层纹理
        // material.alphaMap = await textureLoader.loadAsync('/textures/earth_clouds.png');
        
        return new THREE.Mesh(geometry, material);
    }
    
    /**
     * 判断行星是否有明显大气
     */
    private hasMajorAtmosphere(planetData: PlanetConfig): boolean {
        return ['EAR', 'VEN', 'MAR', 'JUP', 'SAT', 'URA', 'NEP'].includes(planetData.id);
    }
    
    /**
     * 更新动画
     */
    public update(deltaTime: number): void {
        if (this.planetMesh) {
            // 行星自转
            this.planetMesh.rotation.y += deltaTime * 0.05;
        }
        
        if (this.cloudsMesh) {
            // 云层略快于行星自转
            this.cloudsMesh.rotation.y += deltaTime * 0.06;
        }
    }
    
    /**
     * 清除当前行星
     */
    private clearPlanet(): void {
        if (this.currentPlanet) {
            this.container.remove(this.currentPlanet);
            
            // 清理资源
            this.currentPlanet.traverse((child: any) => {
                if (child.geometry) child.geometry.dispose();
                if (child.material) {
                    if (Array.isArray(child.material)) {
                        child.material.forEach((m: any) => m.dispose());
                    } else {
                        child.material.dispose();
                    }
                }
            });
            
            this.currentPlanet = null;
            this.planetMesh = null;
            this.atmosphereMesh = null;
            this.cloudsMesh = null;
        }
    }
    
    /**
     * 获取当前行星数据
     */
    public getCurrentPlanet(): PlanetConfig | null {
        return this.planetData;
    }
    
    /**
     * 清理
     */
    public dispose(): void {
        this.clearPlanet();
        this.scene.remove(this.container);
    }
}
