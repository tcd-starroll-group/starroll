import * as THREE from 'three';
import { ConstellationData, StarData } from '../../types/constellation';
import { AstroCoordinates } from '../astronomy/Coordinates';
import { ConstellationFactory } from './ConstellationFactory';
import { ConstellationLineMaterial } from '../materials/ConstellationMaterials';
import { createStarPointMaterial } from '../materials/Shaders';

/**
 * 星座系统渲染器
 * 负责：绘制星点、连线、3D 低多边形模型
 */
export class ConstellationRenderer {
    public scene: THREE.Scene;
    
    // 资源管理
    private groups: Map<string, THREE.Group> = new Map(); // 每个星座一个 Group
    private starsGeometry: THREE.BufferGeometry | null = null;
    private starsMaterial: THREE.ShaderMaterial | null = null;
    
    // 状态
    private mode: 'all' | 'single' | 'none' = 'all';
    private focusedId: string | null = null;

    constructor(scene: THREE.Scene) {
        this.scene = scene;
    }

    /**
     * 加载并生成星座（异步版本，支持外部模型）
     */
    public async loadConstellations(dataList: ConstellationData[]) {
        // 1. 全局星点图层 (所有星座的星点合并为一个粒子系统，提高性能)
        this.createGlobalStarLayer(dataList);

        // 2. 为每个星座创建独立的 Group (包含连线 + 3D 模型 + 标签)
        const promises = dataList.map(async (data) => {
            const group = new THREE.Group();
            
            // A. 创建连线
            const lines = this.createLines(data);
            group.add(lines);

            // B. 创建 3D 象征模型（异步加载，支持外部GLTF模型）
            // 计算星座中心的世界坐标
            const center = AstroCoordinates.raDecToVector3(data.center.ra, data.center.dec, 450); // 稍微比星星近一点
            const model = await ConstellationFactory.createShapeAsync(data.shapeId, 30, data.id);
            model.position.copy(center);
            model.lookAt(0, 0, 0); // 面向中心
            
            // 默认隐藏模型，只有 hover/focus 时显示，或者根据模式显示
            model.visible = true; 
            group.add(model);
            group.userData.model = model; // 保存引用

            // C. 标签 (暂略，可后续添加 CSS2D)

            this.scene.add(group);
            this.groups.set(data.id, group);
        });

        // 等待所有模型加载完成
        await Promise.all(promises);
    }

    /**
     * 创建全局星点层
     */
    private createGlobalStarLayer(dataList: ConstellationData[]) {
        const allStars: StarData[] = [];
        dataList.forEach(c => allStars.push(...c.stars));

        const geometry = new THREE.BufferGeometry();
        const positions: number[] = [];
        const sizes: number[] = [];
        const colors: number[] = []; // 预留

        allStars.forEach(star => {
            const radius = 500; // 天球半径
            const pos = AstroCoordinates.raDecToVector3(star.ra, star.dec, radius);
            positions.push(pos.x, pos.y, pos.z);
            
            // 视星等转换大小: mag 越小越亮。 mag 1 ~ 6
            // size = (6 - mag) * scale
            const size = Math.max(0.5, (6 - star.mag)) * 2.0;
            sizes.push(size);
        });

        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('aScale', new THREE.Float32BufferAttribute(sizes, 1));

        this.starsMaterial = createStarPointMaterial(0xffffff);
        // 星星不随距离衰减太大，保持可见
        this.starsMaterial.uniforms.uSize.value = 4.0; 

        const starPoints = new THREE.Points(geometry, this.starsMaterial);
        this.scene.add(starPoints);
        this.starsGeometry = geometry;
    }

    /**
     * 创建单个星座的连线
     */
    private createLines(data: ConstellationData): THREE.LineSegments {
        const geometry = new THREE.BufferGeometry();
        const positions: number[] = [];
        const radius = 500;

        data.lines.forEach(pair => {
            const s1 = data.stars[pair[0]];
            const s2 = data.stars[pair[1]];
            
            if (s1 && s2) {
                const p1 = AstroCoordinates.raDecToVector3(s1.ra, s1.dec, radius);
                const p2 = AstroCoordinates.raDecToVector3(s2.ra, s2.dec, radius);
                positions.push(p1.x, p1.y, p1.z);
                positions.push(p2.x, p2.y, p2.z);
            }
        });

        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        return new THREE.LineSegments(geometry, ConstellationLineMaterial);
    }

    public update(deltaTime: number) {
        // 更新材质时间 (呼吸效果)
        this.groups.forEach(group => {
            const model = group.userData.model as THREE.Group;
            if (model && model.visible) {
                // 更新子 Mesh 的 material uniform
                model.children.forEach((mesh: any) => {
                    if (mesh.material && mesh.material.uniforms) {
                        mesh.material.uniforms.uTime.value += deltaTime;
                    }
                });
                
                // 轻微自转
                model.rotation.y += deltaTime * 0.1;
            }
        });
        
        // 更新星点闪烁
        if (this.starsMaterial) {
            this.starsMaterial.uniforms.uTime.value += deltaTime;
        }
    }

    public setVisibleMode(mode: 'all' | 'single' | 'none') {
        this.mode = mode;
        this.groups.forEach(g => {
            g.visible = (mode === 'all');
        });
    }

    public getGroup(id: string) {
        return this.groups.get(id);
    }
}

