import * as THREE from 'three';
import { ConstellationShapeId } from '../../types/constellation';
import { GlassConstellationMaterial } from '../materials/ConstellationMaterials';
import { ModelLoader } from '../utils/GLTFLoader';

/**
 * 星座 3D 形状工厂
 * 根据抽象 ID 生成低多边形几何体或加载外部 GLTF 模型
 */
export class ConstellationFactory {
    
    // 星座 ID 到模型文件路径的映射
    // 如果配置了模型路径，将优先使用外部模型
    private static modelPaths: Map<string, string> = new Map([
        // 示例：['CYG', '/models/cygnus.gltf'],
        // 您可以在这里添加更多星座的模型路径
    ]);

    /**
     * 设置星座的外部模型路径
     * @param constellationId 星座ID（如 'CYG'）
     * @param modelPath 模型文件路径（相对于 public 目录，如 '/models/aries.gltf'）
     */
    public static setModelPath(constellationId: string, modelPath: string): void {
        this.modelPaths.set(constellationId, modelPath);
    }

    /**
     * 创建对应的 3D 模型 Mesh（异步版本，支持加载外部模型）
     * @param shapeId 形状 ID
     * @param scale 基础缩放大小
     * @param constellationId 星座ID，用于查找外部模型
     */
    public static async createShapeAsync(
        shapeId: ConstellationShapeId, 
        scale: number = 20,
        constellationId?: string
    ): Promise<THREE.Group> {
        const group = new THREE.Group();

        // 检查是否有外部模型配置
        if (constellationId && this.modelPaths.has(constellationId)) {
            try {
                const modelPath = this.modelPaths.get(constellationId)!;
                const model = await ModelLoader.loadModel(modelPath);
                
                // 调整模型缩放
                model.scale.setScalar(scale);
                
                // 应用玻璃材质到模型的所有子网格
                this.applyMaterialToModel(model, GlassConstellationMaterial.clone());
                
                group.add(model);
                group.userData = { isExternalModel: true };
                
                return group;
            } catch (error) {
                console.warn(`Failed to load external model for ${constellationId}, falling back to procedural geometry`, error);
                // 加载失败时使用程序生成的几何体
            }
        }

        // 使用程序生成的几何体（同步版本的逻辑）
        return this.createShape(shapeId, scale);
    }
    
    /**
     * 创建对应的 3D 模型 Mesh（同步版本，仅程序生成）
     * @param shapeId 形状 ID
     * @param scale 基础缩放大小
     */
    public static createShape(shapeId: ConstellationShapeId, scale: number = 20): THREE.Group {
        const group = new THREE.Group();
        
        // 材质克隆，因为可能需要单独控制 uniform
        const material = GlassConstellationMaterial.clone();
        
        let geometry: THREE.BufferGeometry;

        // 根据 ID 拼装不同的几何体
        // 这里使用简单的几何体组合来"意象化"星座
        switch (shapeId) {
            case 'bird': // 天鹅、天鹰
                geometry = this.createBirdGeometry();
                break;
            case 'lion': // 狮子
            case 'bear': // 大熊
                geometry = this.createBeastGeometry();
                break;
            case 'human': // 猎户、仙女
                geometry = this.createHumanGeometry();
                break;
            case 'triangle':
                geometry = new THREE.ConeGeometry(1, 2, 4); // 四面体
                break;
            case 'cross': // 北十字
                geometry = this.createCrossGeometry();
                break;
            default:
                geometry = new THREE.IcosahedronGeometry(1, 0); // 默认 20 面体
        }

        const mesh = new THREE.Mesh(geometry, material);
        mesh.scale.setScalar(scale);
        
        // 随机一点旋转，让它看起来不那么死板
        mesh.rotation.z = Math.random() * 0.5;
        mesh.rotation.x = Math.random() * 0.5;

        group.add(mesh);
        
        // 保存材质引用以便更新 time
        group.userData = { material }; 
        
        return group;
    }

    /**
     * 应用材质到模型的所有网格
     */
    private static applyMaterialToModel(model: THREE.Group, material: THREE.Material): void {
        model.traverse((child: any) => {
            if (child.isMesh) {
                const mesh = child as THREE.Mesh;
                mesh.material = material;
            }
        });
    }

    // --- 几何体生成器 ---

    private static createBirdGeometry(): THREE.BufferGeometry {
        // 模拟鸟：一个细长的圆锥做身体，两个扁平的圆锥做翅膀
        const body = new THREE.ConeGeometry(0.5, 3, 5);
        body.rotateX(Math.PI / 2); // 水平
        
        const leftWing = new THREE.ConeGeometry(0.5, 2.5, 4);
        leftWing.scale(1, 0.2, 1); // 压扁
        leftWing.translate(0, 0, 1.2);
        leftWing.rotateZ(Math.PI / 3);

        const rightWing = leftWing.clone();
        rightWing.scale(1, 1, -1); // 镜像
        
        // 合并 (Three.js BufferGeometryUtils.mergeBufferGeometries 需要引入 utils，这里我们简化，只返回身体示意)
        // 实际项目中建议使用 merge，或者返回一个 Group 包含多个 Mesh
        // 这里为了简化，我们返回一个更抽象的形状：扁平的菱形体
        
        const geometry = new THREE.OctahedronGeometry(1, 0);
        geometry.scale(1, 0.5, 2); // 压扁拉长
        return geometry;
    }

    private static createBeastGeometry(): THREE.BufferGeometry {
        // 兽类：前后两个部分
        const geometry = new THREE.BoxGeometry(1.5, 1, 2.5);
        // 稍微扭曲一下顶点做 Low-poly 效果？
        // 暂时直接返回盒子
        return geometry;
    }

    private static createHumanGeometry(): THREE.BufferGeometry {
        // 人形：类似沙漏形状
        const geometry = new THREE.CylinderGeometry(0.5, 0.5, 3, 5);
        return geometry;
    }

    private static createCrossGeometry(): THREE.BufferGeometry {
        // 十字架
        const geometry = new THREE.BoxGeometry(0.5, 3, 0.5);
        // 还需要横梁，但单个 geometry 比较难做，这里简化为长条
        return geometry;
    }
}
