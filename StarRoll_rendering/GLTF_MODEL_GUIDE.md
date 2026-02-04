# GLTF 模型使用指南

本指南介绍如何将从 Sketchfab 等网站下载的 GLTF 模型替换到项目中的星座模型。

## 步骤 1: 下载 GLTF 模型

1. 访问 Sketchfab 或其他 3D 模型网站
2. 搜索你想要的模型（例如：白羊座、天鹅座等）
3. 下载 GLTF 格式的模型文件
   - 推荐下载 `.gltf` 格式（包含纹理）或 `.glb` 格式（单文件）
4. 解压下载的文件

## 步骤 2: 放置模型文件

将下载的模型文件放到项目的 `public/models/` 目录下：

```
StarRoll_副本/
├── public/
│   └── models/
│       ├── cygnus.gltf          # 天鹅座模型
│       ├── cygnus.bin           # 模型数据（如果有）
│       ├── textures/            # 纹理文件夹（如果有）
│       │   ├── texture1.png
│       │   └── texture2.png
│       └── aries.glb            # 白羊座模型（单文件格式）
```

## 步骤 3: 配置模型路径

在 `src/main.ts` 或应用初始化的地方，添加模型配置：

### 方法 A: 在 main.ts 中配置

```typescript
import { ConstellationFactory } from './core/renderer/ConstellationFactory';

// 配置星座模型路径
ConstellationFactory.setModelPath('CYG', '/models/cygnus.gltf');  // 天鹅座
ConstellationFactory.setModelPath('ORI', '/models/orion.glb');    // 猎户座（如果有）
// 添加更多星座...
```

### 方法 B: 创建配置文件

创建 `src/config/models.ts`：

```typescript
import { ConstellationFactory } from '../core/renderer/ConstellationFactory';

export function initializeModels() {
    // 配置所有星座的外部模型
    ConstellationFactory.setModelPath('CYG', '/models/cygnus.gltf');
    ConstellationFactory.setModelPath('ARI', '/models/aries.glb');
    // 添加更多...
}
```

然后在 `main.ts` 中调用：

```typescript
import { initializeModels } from './config/models';

// 在创建渲染器之前配置模型
initializeModels();
```

## 步骤 4: 调整模型大小和方向（可选）

如果模型看起来太大或太小，你可以在配置时调整缩放值。

修改 `src/core/renderer/ConstellationRenderer.ts` 第 46 行：

```typescript
// 调整第三个参数来改变模型大小
const model = await ConstellationFactory.createShapeAsync(data.shapeId, 30, data.id);
// 例如：将 30 改为 50 会让模型更大
```

## 常见问题

### Q: 模型不显示怎么办？
A: 
1. 检查浏览器控制台是否有错误信息
2. 确认模型文件路径正确
3. 确认模型文件格式是 `.gltf` 或 `.glb`
4. 尝试在浏览器中直接访问模型文件 URL（如 `http://localhost:5173/models/cygnus.gltf`）

### Q: 模型颜色不对怎么办？
A: 
项目会自动将玻璃材质应用到模型上。如果想保留原始材质，需要修改 `ConstellationFactory.ts` 中的 `createShapeAsync` 方法，注释掉这一行：

```typescript
// this.applyMaterialToModel(model, GlassConstellationMaterial.clone());
```

### Q: 模型方向不对怎么办？
A: 
在 `ConstellationFactory.ts` 的 `createShapeAsync` 方法中，在 `group.add(model)` 之前添加旋转：

```typescript
model.rotation.x = Math.PI / 2; // 绕X轴旋转90度
model.rotation.y = Math.PI / 4; // 绕Y轴旋转45度
```

### Q: 如何只替换天鹅座模型？
A: 
只需配置天鹅座的模型路径，其他星座会继续使用程序生成的几何体：

```typescript
ConstellationFactory.setModelPath('CYG', '/models/cygnus.gltf');
```

## 星座ID对照表

| 星座中文名 | 星座ID | 英文名 |
|-----------|--------|--------|
| 天鹅座 | CYG | Cygnus |
| 猎户座 | ORI | Orion |
| 白羊座 | ARI | Aries |
| 金牛座 | TAU | Taurus |
| 双子座 | GEM | Gemini |
| 巨蟹座 | CNC | Cancer |
| 狮子座 | LEO | Leo |
| 处女座 | VIR | Virgo |
| 天秤座 | LIB | Libra |
| 天蝎座 | SCO | Scorpius |
| 射手座 | SGR | Sagittarius |
| 摩羯座 | CAP | Capricornus |
| 水瓶座 | AQR | Aquarius |
| 双鱼座 | PSC | Pisces |

注意：项目目前只包含猎户座(ORI)和天鹅座(CYG)的数据。如需添加更多星座，请修改 `src/core/data/constellations.ts`。
