import * as THREE from 'three';
import { createTwinkleStarMaterial } from '../materials/GalaxyShaders';
import { 
    NebulaType,
    createSpiralNebula,
    createFilamentNebula,
    createExplosiveNebula,
    createLayeredNebula,
    createDarkNebula,
    createDeepPurpleNebula,
    createDeepSpaceGrid
} from './background/NebulaVariants';

/**
 * 银河背景渲染器
 * 负责渲染：
 * 1. 程序化星云天空盒 (Nebula Sphere)
 * 2. 大规模背景恒星点云 (Star Field)
 */
export class GalaxyBackgroundRenderer {
    private scene: THREE.Scene;
    private nebulaMesh: THREE.Mesh | null = null;
    private starSystem: THREE.Points | null = null;
    private nebulaMaterial: THREE.ShaderMaterial | null = null;
    private starsMaterial: THREE.ShaderMaterial | null = null;
    
    // 当前星云类型
    private currentType: NebulaType = 'spiral';

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.init();
    }

    private init() {
        // 1. 创建星云球 (最远层)
        // 初始默认为 Spiral
        this.setNebulaType('spiral');

        // 2. 创建恒星粒子云 (中间层)
        this.createStarField();
    }
    
    /**
     * 切换星云风格
     */
    public setNebulaType(type: NebulaType) {
        this.currentType = type;
        
        // 销毁旧材质
        if (this.nebulaMaterial) {
            this.nebulaMaterial.dispose();
        }
        if (this.nebulaMesh) {
            this.scene.remove(this.nebulaMesh);
            this.nebulaMesh.geometry.dispose();
        }
        
        // 创建新材质
        switch (type) {
            case 'filament':
                this.nebulaMaterial = createFilamentNebula();
                break;
            case 'explosive':
                this.nebulaMaterial = createExplosiveNebula();
                break;
            case 'layered':
                this.nebulaMaterial = createLayeredNebula();
                break;
            case 'dark':
                this.nebulaMaterial = createDarkNebula();
                break;
            case 'purple':
                this.nebulaMaterial = createDeepPurpleNebula();
                break;
            case 'deepspace':
                this.nebulaMaterial = createDeepSpaceGrid();
                break;
            case 'spiral':
            default:
                this.nebulaMaterial = createSpiralNebula();
                break;
        }
        
        const nebulaGeo = new THREE.SphereGeometry(40000, 64, 64);
        this.nebulaMesh = new THREE.Mesh(nebulaGeo, this.nebulaMaterial);
        this.nebulaMesh.renderOrder = -100;
        this.scene.add(this.nebulaMesh);
    }

    private createStarField() {
        // 数量：20,000 颗足以模拟壮观星空
        const starCount = 20000;
        const starGeo = new THREE.BufferGeometry();
        
        const positions: number[] = [];
        const colors: number[] = [];
        const sizes: number[] = [];
        const phases: number[] = [];
        const speeds: number[] = [];

        const colorPalette = [
            new THREE.Color(0x9bb0ff), // O型 - 蓝白
            new THREE.Color(0xaabfff), // B型 - 蓝白
            new THREE.Color(0xcad7ff), // A型 - 白
            new THREE.Color(0xf8f7ff), // F型 - 黄白
            new THREE.Color(0xfff4ea), // G型 - 黄 (太阳)
            new THREE.Color(0xffd2a1), // K型 - 橙
            new THREE.Color(0xffcc6f)  // M型 - 红
        ];

        for (let i = 0; i < starCount; i++) {
            // A. 位置分布：球壳分布
            // 半径在 30000 ~ 38000 之间
            const r = 30000 + Math.random() * 8000;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos((Math.random() * 2) - 1);
            
            const x = r * Math.sin(phi) * Math.cos(theta);
            const y = r * Math.sin(phi) * Math.sin(theta);
            const z = r * Math.cos(phi);
            
            positions.push(x, y, z);

            // B. 颜色：加权随机
            const colorIndex = Math.floor(Math.random() * colorPalette.length);
            const c = colorPalette[colorIndex];
            // 稍微随机化一点亮度
            const brightness = 0.8 + Math.random() * 0.2;
            colors.push(c.r * brightness, c.g * brightness, c.b * brightness);

            // C. 大小 (Mag)：大部分星星很小，少数很大
            // pow(random, 4) 让大数值的概率极低
            const sizeBase = Math.random();
            const size = Math.pow(sizeBase, 4.0) * 4.0 + 0.5; // 0.5 ~ 4.5
            sizes.push(size);

            // D. 闪烁参数
            phases.push(Math.random() * Math.PI * 2);
            speeds.push(1.0 + Math.random() * 3.0); // 闪烁速度
        }

        starGeo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        starGeo.setAttribute('aColor', new THREE.Float32BufferAttribute(colors, 3));
        starGeo.setAttribute('aSize', new THREE.Float32BufferAttribute(sizes, 1));
        starGeo.setAttribute('aPhase', new THREE.Float32BufferAttribute(phases, 1));
        starGeo.setAttribute('aSpeed', new THREE.Float32BufferAttribute(speeds, 1));

        this.starsMaterial = createTwinkleStarMaterial();
        this.starSystem = new THREE.Points(starGeo, this.starsMaterial);
        
        // 渲染顺序：在星云之上，在普通物体之下
        this.starSystem.renderOrder = -99;
        this.scene.add(this.starSystem);
    }

    public update(deltaTime: number) {
        if (this.nebulaMaterial) {
            this.nebulaMaterial.uniforms.uTime.value += deltaTime;
        }
        if (this.starsMaterial) {
            this.starsMaterial.uniforms.uTime.value += deltaTime;
        }
    }
}

