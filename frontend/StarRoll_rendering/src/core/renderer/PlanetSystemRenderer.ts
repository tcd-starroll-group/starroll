import * as THREE from 'three';
import { PlanetConfig } from '../../types/planet';
import { createPlanetMaterial, createSunMaterial, createStarPointMaterial } from '../materials/Shaders';
// 如果未来有 OrbitControls，可以在这里引入，或者由外部传入 camera 控制

/**
 * 行星系统核心渲染器
 * 负责管理：场景、相机、所有天体对象、动画循环
 */
export class PlanetSystemRenderer {
    // --- 核心 Three.js 组件 ---
    public scene: THREE.Scene;
    public camera: THREE.PerspectiveCamera;
    public renderer: THREE.WebGLRenderer;
    
    // --- 内部状态管理 ---
    public planets: Map<string, { mesh: THREE.Mesh, config: PlanetConfig, orbitLines?: THREE.Line, angle: number }> = new Map();
    private sunMesh: THREE.Mesh | null = null;
    private materials: THREE.Material[] = []; // 用于清理资源
    private geometries: THREE.BufferGeometry[] = []; // 用于清理资源

    // --- 动画控制 ---
    private timeScale: number = 1.0; // 时间流速倍率
    private isPaused: boolean = false;

    /**
     * 构造函数：初始化基础 3D 环境
     * @param container 挂载 Canvas 的 DOM 容器
     */
    constructor(container: HTMLElement) {
        // 1. 创建场景
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000510); // 深空蓝黑背景
        // 添加环境雾，增加深邃感
        this.scene.fog = new THREE.FogExp2(0x000510, 0.002);

        // 2. 创建相机
        const width = container.clientWidth;
        const height = container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 50000);
        this.camera.position.set(0, 200, 400); // 初始俯视视角
        this.camera.lookAt(0, 0, 0);

        // 3. 创建渲染器
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true, // 抗锯齿
            alpha: true,     // 透明背景支持
            logarithmicDepthBuffer: true // 防止远距离 z-fighting
        });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        
        // 开启阴影贴图 (虽然在宇宙中主要是自阴影，但也加上)
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        // 将 Canvas 添加到 DOM
        container.appendChild(this.renderer.domElement);

        // 4. 添加基础光照 (环境光 + 太阳点光源)
        const ambientLight = new THREE.AmbientLight(0x333333); // 微弱环境光
        this.scene.add(ambientLight);

        // 太阳光 (点光源) - 位于中心 (0,0,0)
        const sunLight = new THREE.PointLight(0xffffff, 2.0, 5000);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 2048;
        sunLight.shadow.mapSize.height = 2048;
        this.scene.add(sunLight);

        // 5. 初始化背景星空
        // 已移除：由外部 GalaxyBackgroundRenderer 接管
        // this.createStarField();

        // 监听窗口大小变化
        window.addEventListener('resize', this.onResize.bind(this));
    }

    /**
     * 初始化所有行星数据
     * @param configs 行星配置列表
     */
    public init(configs: PlanetConfig[]) {
        // 清理旧数据 (如果有)
        this.dispose();

        // 1. 创建太阳 (假设 ID 为 'sun' 或者特殊处理)
        // 这里我们简单约定：如果 type 是 'star' 且 radius 很大，就是太阳
        // 或者调用者显式包含太阳配置。通常太阳在 (0,0,0)。
        
        // 我们遍历配置
        configs.forEach(config => {
            if (config.type === 'star') {
                this.createSun(config);
            } else {
                this.createPlanet(config);
            }
        });
    }

    /**
     * 创建太阳
     */
    private createSun(config: PlanetConfig) {
        const geometry = new THREE.SphereGeometry(config.radius, 64, 64);
        const material = createSunMaterial(); // 使用自定义 Shader 材质
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(0, 0, 0);
        
        // 太阳通常不需要投射阴影(它是光源)，但可能遮挡背后的东西
        
        this.scene.add(mesh);
        this.sunMesh = mesh;
        
        // 注册资源以便清理
        this.geometries.push(geometry);
        this.materials.push(material);

        // 添加一个光晕 Sprite (Billboard) 增强发光感
        const spriteMaterial = new THREE.SpriteMaterial({ 
            map: this.createGlowTexture(), 
            color: 0xffaa00, 
            transparent: true, 
            blending: THREE.AdditiveBlending 
        });
        const sprite = new THREE.Sprite(spriteMaterial);
        sprite.scale.set(config.radius * 6, config.radius * 6, 1);
        mesh.add(sprite);
    }

    /**
     * 创建单个行星 (Mesh + 轨道 + 光环)
     */
    private createPlanet(config: PlanetConfig) {
        // 1. 创建行星本体 Mesh
        const geometry = new THREE.SphereGeometry(config.radius, 64, 64);
        
        // 使用配置中的 visual 参数，或者默认值
        const material = createPlanetMaterial({
            color: config.color,
            noiseScale: config.visual?.noiseScale,
            noiseStrength: config.visual?.noiseStrength,
            rimPower: config.visual?.rimPower
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;

        // 2. 创建光环 (如果配置有)
        if (config.hasRings && config.ringConfig) {
            this.createPlanetRings(mesh, config.ringConfig);
        }

        // 3. 创建轨道线 (Visual)
        const orbitLine = this.createOrbitLine(config.orbitRadius);
        this.scene.add(orbitLine);

        // 4. 将行星添加到场景
        // 初始位置：x = 半径 (简单起见，从 x 轴开始)
        mesh.position.set(config.orbitRadius, 0, 0);
        this.scene.add(mesh);

        // 5. 存储引用，用于 update 循环更新位置
        this.planets.set(config.id, {
            mesh,
            config,
            orbitLines: orbitLine,
            angle: Math.random() * Math.PI * 2 // 随机初始角度
        });
        
        this.geometries.push(geometry);
        this.materials.push(material);
    }

    /**
     * 创建粒子光环
     * 优化版：使用非均匀分布模拟环缝结构
     */
    private createPlanetRings(planetMesh: THREE.Mesh, ringConfig: NonNullable<PlanetConfig['ringConfig']>) {
        const { innerRadius, outerRadius, color, count = 2000 } = ringConfig;

        // 使用 BufferGeometry 存储粒子位置
        const geometry = new THREE.BufferGeometry();
        const positions: number[] = [];
        const scales: number[] = []; 
        
        for (let i = 0; i < count; i++) {
            // 在圆环区域内分布
            // 使用 sqrt 保证面积均匀分布，避免内圈过密
            // 增加一些随机环缝：通过正弦函数剔除部分粒子
            let r: number;
            let valid = false;
            
            // 简单的拒绝采样，尝试几次生成合法半径
            for(let k=0; k<5; k++) {
                const rnd = Math.random();
                // r = sqrt(rnd * (R_out^2 - R_in^2) + R_in^2)
                const rSq = rnd * (outerRadius*outerRadius - innerRadius*innerRadius) + innerRadius*innerRadius;
                r = Math.sqrt(rSq);
                
                // 模拟卡西尼缝 (Cassini Division) - 在特定半径处降低密度
                // 简单地用 sin 函数模拟几条缝隙
                const normalizedR = (r - innerRadius) / (outerRadius - innerRadius);
                const density = 0.5 + 0.5 * Math.sin(normalizedR * 20.0); // 波动密度
                
                if (Math.random() < density) {
                    valid = true;
                    break;
                }
            }
            if (!valid) continue; // 放弃这个粒子，虽然会导致总数略少，但分布更好

            const theta = Math.random() * Math.PI * 2;
            
            // @ts-ignore
            const x = r * Math.cos(theta);
            // @ts-ignore
            const z = r * Math.sin(theta);
            // 垂直厚度非常薄
            const y = (Math.random() - 0.5) * 0.2; 

            positions.push(x, y, z);
            
            // 粒子大小随机，模拟大小不一的冰块
            scales.push(Math.random() * 0.8 + 0.2); 
        }

        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('aScale', new THREE.Float32BufferAttribute(scales, 1));

        // 使用自定义星点材质，稍微调亮
        const material = createStarPointMaterial(color);
        material.uniforms.uSize.value = 3.0; // 稍大一点，配合高透明度

        const points = new THREE.Points(geometry, material);
        
        // 稍微倾斜一点光环
        points.rotation.x = Math.PI * 0.1; 
        points.rotation.z = Math.PI * 0.05;

        planetMesh.add(points); 
        
        this.geometries.push(geometry);
        this.materials.push(material);
    }

    /**
     * 创建轨道线可视化
     */
    private createOrbitLine(radius: number): THREE.Line {
        const segments = 128;
        const geometry = new THREE.BufferGeometry();
        const positions: number[] = [];

        for (let i = 0; i <= segments; i++) {
            const theta = (i / segments) * Math.PI * 2;
            positions.push(
                Math.cos(theta) * radius,
                0,
                Math.sin(theta) * radius
            );
        }

        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        
        const material = new THREE.LineBasicMaterial({ 
            color: 0xffffff, 
            transparent: true, 
            opacity: 0.15 // 非常淡的轨道线
        });

        const line = new THREE.Line(geometry, material);
        line.rotation.x = Math.PI / 2; // 如果是 X-Y 平面圆，需要旋转。这里我们直接画在 X-Z 平面，无需旋转
        // 上面 push 的 y 是 0，所以默认就是 X-Z 平面 (水平面)
        
        return line;
    }

    /**
     * 创建背景星空 (点云)
     */
    private createStarField() {
        const count = 5000;
        const geometry = new THREE.BufferGeometry();
        const positions: number[] = [];
        const scales: number[] = [];

        for (let i = 0; i < count; i++) {
            // 在很大的球体内随机分布
            const r = 2000 + Math.random() * 2000;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos((Math.random() * 2) - 1);

            const x = r * Math.sin(phi) * Math.cos(theta);
            const y = r * Math.sin(phi) * Math.sin(theta);
            const z = r * Math.cos(phi);

            positions.push(x, y, z);
            scales.push(Math.random() * 1.5 + 0.5);
        }

        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('aScale', new THREE.Float32BufferAttribute(scales, 1));

        const material = createStarPointMaterial(0xeeeeee);
        const stars = new THREE.Points(geometry, material);
        this.scene.add(stars);
        
        this.geometries.push(geometry);
        this.materials.push(material);
    }

    /**
     * 辅助：创建程序化光晕贴图
     */
    private createGlowTexture(): THREE.Texture {
        const canvas = document.createElement('canvas');
        canvas.width = 64;
        canvas.height = 64;
        const context = canvas.getContext('2d')!;
        const gradient = context.createRadialGradient(32, 32, 0, 32, 32, 32);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        gradient.addColorStop(0.2, 'rgba(255, 200, 100, 0.8)');
        gradient.addColorStop(0.5, 'rgba(255, 100, 50, 0.2)');
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
        context.fillStyle = gradient;
        context.fillRect(0, 0, 64, 64);
        const texture = new THREE.CanvasTexture(canvas);
        return texture;
    }

    /**
     * 每一帧的更新逻辑
     * @param deltaTime 距离上一帧的时间 (秒)
     */
    public update(deltaTime: number) {
        if (this.isPaused) return;

        const dt = deltaTime * this.timeScale;

        // 1. 更新材质 Uniforms (Time)
        // 简单方式：遍历所有材质，如果有 uTime 就更新
        // 为了性能，最好维护一个 shaderMaterial 列表。这里简化处理。
        this.materials.forEach((mat: any) => {
            if (mat.uniforms && mat.uniforms.uTime) {
                mat.uniforms.uTime.value += dt;
            }
        });

        // 2. 更新行星位置 (公转 & 自转)
        this.planets.forEach((data, id) => {
            const { mesh, config, angle } = data;
            
            // --- 公转 (Revolution) ---
            // 简单的圆周运动：angle += speed * dt
            // speed ~ 1 / period
            // 加上一个基础速度因子 0.5 让他动起来不至于太慢
            const orbitSpeed = (1.0 / config.orbitPeriod) * 0.5; 
            data.angle += orbitSpeed * dt;
            
            mesh.position.x = Math.cos(data.angle) * config.orbitRadius;
            mesh.position.z = Math.sin(data.angle) * config.orbitRadius;

            // --- 自转 (Rotation) ---
            // 自转速度 ~ 1 / rotationPeriod
            if (config.rotationPeriod > 0) {
                const rotSpeed = (1.0 / config.rotationPeriod) * 2.0;
                mesh.rotation.y += rotSpeed * dt;
            }
        });

        // 3. 渲染场景
        this.renderer.render(this.scene, this.camera);
    }

    /**
     * 窗口大小调整
     */
    public onResize() {
        const parent = this.renderer.domElement.parentElement;
        if (!parent) return;
        
        const width = parent.clientWidth;
        const height = parent.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    /**
     * 销毁实例，清理内存
     */
    public dispose() {
        // 清理几何体
        this.geometries.forEach(g => g.dispose());
        this.geometries = [];

        // 清理材质
        this.materials.forEach(m => m.dispose());
        this.materials = [];

        // 清理场景对象
        while(this.scene.children.length > 0){ 
            this.scene.remove(this.scene.children[0]); 
        }
        
        this.renderer.dispose();
    }
    
    // API: 控制
    public setTimeScale(scale: number) { this.timeScale = scale; }
    public pause() { this.isPaused = true; }
    public resume() { this.isPaused = false; }
    
    public getPlanet(id: string) {
        if (id === 'sun' && this.sunMesh) {
            // 临时封装一个符合格式的对象，但注意 sun 没有 angle 和 orbitLines
            return {
                mesh: this.sunMesh,
                config: { id: 'sun', orbitRadius: 0 } as PlanetConfig,
                angle: 0
            };
        }
        return this.planets.get(id);
    }
}

