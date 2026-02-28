import { ConstellationFactory } from '../core/renderer/ConstellationFactory';

/**
 * 配置星座的外部 GLTF 模型
 * 
 * 使用方法：
 * 1. 将 GLTF/GLB 模型文件放到 public/models/ 目录
 * 2. 在下面添加模型路径配置
 * 3. 在 main.ts 中调用 initializeModels()
 */
export function initializeModels() {
    // 示例：配置天鹅座使用外部模型
    ConstellationFactory.setModelPath('CYG', '/models/andromeda-constellation.gltf');
    
    // 示例：配置白羊座使用外部模型
    // ConstellationFactory.setModelPath('ARI', '/models/aries.glb');
    
    // 添加更多星座模型配置...
    // ConstellationFactory.setModelPath('星座ID', '/models/模型文件名.gltf');
}

/**
 * 预加载模型（可选）
 * 在应用启动时预先加载模型，避免首次显示时的延迟
 */
export async function preloadModels() {
    // 如果有需要预加载的模型，可以在这里添加
    // 例如：
    // await ModelLoader.preloadModels([
    //     '/models/cygnus.gltf',
    //     '/models/aries.glb'
    // ]);
}
