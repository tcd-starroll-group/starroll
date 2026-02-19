# 📷 摄像头AR渲染实现说明

## 功能概述

已实现真实摄像头AR功能，星空将直接渲染在摄像头画面上，就像真实看到天空一样。

## 实现方案

### 技术架构

```
┌─────────────────────────────────────┐
│   HTML Video Element (摄像头画面)    │  ← 后置摄像头
│   z-index: -1 (背景层)              │
├─────────────────────────────────────┤
│   Three.js Canvas (透明)            │  ← 星空渲染
│   background: null                  │
│   alpha: true                       │
└─────────────────────────────────────┘
```

### 核心代码

#### 1. 摄像头启动
```typescript
private async startCamera(): Promise<void> {
    // 创建video元素作为背景
    this.videoElement = document.createElement('video');
    this.videoElement.style.zIndex = '-1';  // 在最底层
    
    // 请求后置摄像头
    const constraints = {
        video: {
            facingMode: 'environment',  // 后置摄像头（重要！）
            width: { ideal: 1920 },
            height: { ideal: 1080 }
        }
    };
    
    // 获取视频流
    this.videoStream = await navigator.mediaDevices.getUserMedia(constraints);
    this.videoElement.srcObject = this.videoStream;
    await this.videoElement.play();
}
```

#### 2. Three.js透明渲染
```typescript
// 启用AR模式时
this.scene.background = null;  // 透明背景
this.renderer.setClearColor(0x000000, 0);  // 完全透明

// 渲染器配置
new THREE.WebGLRenderer({ 
    antialias: true,
    alpha: true  // 启用透明通道
});
```

#### 3. 摄像头关闭
```typescript
private stopCamera(): void {
    // 停止所有视频轨道
    this.videoStream.getTracks().forEach(track => track.stop());
    
    // 移除video元素
    this.videoElement.remove();
}
```

## 使用流程

### 启用AR模式
```
1. 点击 "📱 启用 AR 模式"
2. 允许传感器权限 ✅
3. 允许摄像头权限 ✅
4. 摄像头自动启动，显示真实画面
5. 星空叠加在摄像头画面上
```

### 效果展示
```
┌───────────────────────────────┐
│                               │
│   📹 真实环境（摄像头）        │
│                               │
│      ⭐  ⭐                    │  ← 星星叠加
│         🎭 星座轮廓            │  ← 星座叠加
│   ⭐      ⭐                   │
│                               │
│   [实时追踪设备方向]           │
│                               │
└───────────────────────────────┘
```

### 退出AR模式
```
1. 再次点击按钮关闭AR
2. 摄像头自动关闭 ✅
3. 恢复深色星空背景
```

## 权限要求

### 需要授予的权限

1. **传感器权限** (DeviceOrientation)
   - iOS: Safari 设置 → 隐私 → 动作与方向
   - Android: 通常自动授予

2. **摄像头权限** (Camera)
   - iOS: 设置 → Safari → 相机 → 允许
   - Android: 弹窗点击"允许"

### 权限请求流程
```
用户点击"启用AR"
    ↓
请求传感器权限
    ↓ (成功)
请求摄像头权限
    ↓ (成功)
启动摄像头
    ↓
开始AR渲染
```

## 技术细节

### 摄像头选择

```typescript
facingMode: 'environment'  // 后置摄像头（朝外）
// 而不是 'user' (前置摄像头/自拍)
```

**为什么用后置摄像头？**
- 观星时需要拍摄天空
- 后置摄像头朝向与用户视线一致
- 更符合AR观星的使用场景

### Video元素配置

```typescript
// iOS兼容性配置（重要！）
video.setAttribute('playsinline', '');        // 内联播放
video.setAttribute('webkit-playsinline', ''); // Safari兼容

// 全屏背景样式
video.style.objectFit = 'cover';  // 填充整个屏幕
video.style.zIndex = '-1';        // 在最底层
```

### 分辨率选择

```typescript
width: { ideal: 1920 },   // 理想宽度
height: { ideal: 1080 }   // 理想高度
```

**说明**：
- `ideal` 表示期望值，浏览器会尽量满足
- 如果设备不支持，会自动降级到支持的分辨率
- 实际分辨率可通过 `video.videoWidth/Height` 获取

### 性能优化

#### 1. 避免纹理上传
```typescript
// ❌ 不推荐：使用VideoTexture
const texture = new THREE.VideoTexture(video);
scene.background = texture;  // 每帧上传GPU，性能差

// ✅ 推荐：HTML层叠加
video.style.zIndex = '-1';   // HTML背景
scene.background = null;     // Three.js透明
```

#### 2. 限制分辨率
```typescript
// 根据设备性能调整
const isMobile = /iPhone|iPad|Android/.test(navigator.userAgent);

const width = isMobile ? 1280 : 1920;
const height = isMobile ? 720 : 1080;
```

## FOV保持75度

### 为什么不改变FOV？

```typescript
// FOV = 75° 必须保持
this.camera = new THREE.PerspectiveCamera(75, ...);
```

**原因**：
1. 后续算法依赖此FOV值
2. 星图投影计算基于75度
3. 星座模型缩放基于此FOV

### FOV与摄像头匹配

```javascript
// 摄像头FOV通常在60-80度
// 75度是一个很好的平衡值
// 既不会太宽（失真），也不会太窄（视野小）
```

## 常见问题

### Q: 摄像头画面显示黑屏？

A: 可能的原因：
1. 权限被拒绝 - 检查浏览器设置
2. 摄像头被占用 - 关闭其他使用摄像头的应用
3. iOS需要HTTPS - 使用ngrok等工具

### Q: 画面和星空不对齐？

A: 这是传感器校准问题：
1. 在空旷地方转动手机画"8"字
2. 重启手机
3. 确保使用后置摄像头

### Q: 画面卡顿？

A: 性能优化：
1. 降低摄像头分辨率（720p）
2. 减少渲染的星星数量
3. 关闭不需要的星座模型

### Q: iOS无法启动摄像头？

A: iOS特殊要求：
1. 必须使用Safari浏览器
2. 必须使用HTTPS连接
3. 需要用户手势触发（点击按钮）

## 浏览器兼容性

### 支持的浏览器

| 浏览器 | 支持程度 | 说明 |
|--------|----------|------|
| iOS Safari | ✅ 完全支持 | 需要HTTPS |
| Android Chrome | ✅ 完全支持 | 推荐 |
| Android Firefox | ✅ 完全支持 | - |
| 桌面 Chrome | ✅ 支持 | 可用网络摄像头测试 |
| 微信内置浏览器 | ⚠️ 部分支持 | 权限限制 |

### 检测摄像头支持

```typescript
// 检测是否支持getUserMedia
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    console.log('✅ 支持摄像头API');
} else {
    console.log('❌ 不支持摄像头API');
}
```

## 调试技巧

### 控制台日志

```javascript
// 摄像头启动成功
✅ 摄像头已启动
📹 分辨率: 1920x1080

// 权限错误
❌ 摄像头启动失败: NotAllowedError
用户拒绝了摄像头权限

// 设备错误
❌ 摄像头启动失败: NotFoundError
未找到摄像头设备
```

### 检查视频流

```javascript
// 在浏览器控制台检查
const video = document.querySelector('video');
console.log('视频宽度:', video.videoWidth);
console.log('视频高度:', video.videoHeight);
console.log('播放状态:', video.paused ? '暂停' : '播放中');
```

### 测试后置摄像头

```javascript
// 检查是否使用了后置摄像头
navigator.mediaDevices.enumerateDevices()
    .then(devices => {
        devices.forEach(device => {
            if (device.kind === 'videoinput') {
                console.log(device.label);
            }
        });
    });
```

## 使用示例

### 室内测试
```
1. 打开应用
2. 启用AR模式
3. 摄像头对准墙壁或天花板
4. 看到星空叠加在真实环境上
```

### 室外观星
```
1. 在夜晚使用
2. 启用AR模式
3. 摄像头对准真实夜空
4. 星图与真实星空对齐
5. 帮助识别真实的星座
```

## 安全和隐私

### 隐私保护
- ✅ 视频不会被录制
- ✅ 视频不会被上传
- ✅ 仅用于本地实时显示
- ✅ 关闭AR自动停止摄像头

### 权限管理
- 用户可随时拒绝权限
- 权限请求需要用户交互触发
- 符合浏览器安全策略

---

## 总结

✅ **已实现功能**
- 后置摄像头启动
- 全屏视频背景
- 透明星空叠加
- 自动权限请求
- 优雅的错误处理

✅ **保持的设计**
- FOV = 75° (算法要求)
- 实时传感器追踪
- 高性能渲染

✅ **用户体验**
- 一键启动AR
- 自动申请权限
- 真实摄像头画面
- 星空完美叠加

**现在刷新页面，体验真正的AR星空！** 🌟📷✨
