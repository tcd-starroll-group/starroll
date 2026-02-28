# 模型文件目录

将您下载的 GLTF/GLB 3D 模型文件放在这个目录下。

## 文件格式

支持以下格式：
- `.glb` - 推荐格式（单文件，包含所有资源）
- `.gltf` - 需要配合 `.bin` 和纹理文件

## 示例文件结构

```
models/
├── README.md (本文件)
├── cygnus.glb           # 天鹅座模型（单文件）
├── aries.gltf           # 白羊座模型
├── aries.bin            # 白羊座模型数据
└── textures/            # 纹理文件夹
    ├── aries_texture.png
    └── ...
```

## 模型来源

推荐从以下网站下载免费的 3D 模型：

1. **Sketchfab** - https://sketchfab.com/
   - 搜索：constellation, zodiac, aries, cygnus, leo 等
   - 筛选条件：Downloadable
   - 下载格式：GLTF

2. **Poly Haven** - https://polyhaven.com/models
   - 完全免费的高质量模型

3. **Free3D** - https://free3d.com/
   - 大量免费模型

## 配置模型

下载并放置模型后，需要在代码中配置：

打开 `src/config/models.ts`，添加配置：

```typescript
export function initializeModels() {
    ConstellationFactory.setModelPath('CYG', '/models/cygnus.glb');
    ConstellationFactory.setModelPath('ARI', '/models/aries.glb');
    // 添加更多...
}
```

详细说明请查看项目根目录的 `GLTF_MODEL_GUIDE.md` 和 `QUICK_START.md`。
