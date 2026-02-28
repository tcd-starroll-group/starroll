import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

/**
 * GLTF 模型加载器工具类
 */
export class ModelLoader {
    private static loader = new GLTFLoader();
    private static modelCache: Map<string, THREE.Group> = new Map();

    /**
     * 加载 GLTF 模型
     * @param path 模型文件路径（相对于 public 目录）
     * @returns Promise<THREE.Group>
     */
    public static async loadModel(path: string): Promise<THREE.Group> {
        // 检查缓存
        if (this.modelCache.has(path)) {
            const cached = this.modelCache.get(path)!;
            return cached.clone();
        }

        return new Promise((resolve, reject) => {
            this.loader.load(
                path,
                (gltf: any) => {
                    const model = gltf.scene;
                    
                    // 缓存原始模型
                    this.modelCache.set(path, model);
                    
                    // 返回克隆的模型
                    resolve(model.clone());
                },
                (progress: any) => {
                    // 加载进度（可选）
                    if (progress.total > 0) {
                        console.log(`Loading model: ${(progress.loaded / progress.total * 100).toFixed(2)}%`);
                    }
                },
                (error: any) => {
                    console.error('Error loading model:', error);
                    reject(error);
                }
            );
        });
    }

    /**
     * 预加载多个模型
     * @param paths 模型路径数组
     */
    public static async preloadModels(paths: string[]): Promise<void> {
        const promises = paths.map(path => this.loadModel(path));
        await Promise.all(promises);
    }

    /**
     * 清除缓存
     */
    public static clearCache(): void {
        this.modelCache.clear();
    }
}
