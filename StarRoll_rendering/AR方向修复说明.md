# 🔧 AR方向和变形问题修复

## 问题描述

用户报告的问题：
1. ❌ 手机往下看才能看见星空（应该往上看）
2. ❌ 渲染是一个平面，星星被拉长变形
3. ❌ 方向不对，不是以手机为中心
4. ❌ 仰角显示-79.9°（几乎垂直向下）

## 根本原因

### 1. 传感器数据转换错误

**之前的错误理解**：
```javascript
// 错误：认为 beta = 0 是平视
altitude = -data.beta
```

**iOS DeviceOrientation 实际定义**：
```
手机竖直握持（屏幕朝向你）:
- beta = 0°: 竖直状态
- beta = -90°: 平躺屏幕朝上（看天空）
- beta = 90°: 平躺屏幕朝下（看地面）

观星时的正确状态：
- 手机向上仰，屏幕朝上: beta ≈ -45° 到 -90°
- 此时应该看到星空（altitude > 0）
```

**正确的转换公式**：
```javascript
altitude = data.beta - 90

举例：
- beta = -90° (平躺朝上) → altitude = -180° → 归一化后 90° ✅
- beta = 0° (竖直) → altitude = -90° → 归一化后 0° ✅  
- beta = 90° (平躺朝下) → altitude = 0° → 归一化后 -90° ✅
```

### 2. 相机 lookAt 使用错误

**之前的错误**：
```javascript
// 错误：传入单位方向向量
const direction = new THREE.Vector3(x, y, z)  // 长度≈1
this.camera.lookAt(direction)
```

问题：
- `lookAt` 接受的是**目标点的位置**，不是方向
- 相机在原点(0,0,0)，看向(0.5, 0.5, 0.7)这样的点
- 目标点太近，导致视角扭曲和变形

**正确的做法**：
```javascript
// 正确：计算远处的目标点
const distance = 1000  // 天球半径
const target = new THREE.Vector3(
    direction.x * distance,
    direction.y * distance, 
    direction.z * distance
)
this.camera.lookAt(target)
```

### 3. 视场角(FOV)过大

**之前**：FOV = 75°
- 导致边缘严重变形
- 类似鱼眼镜头效果
- 星星和星座被拉伸

**现在**：FOV = 60°
- 更接近人眼视角
- 减少边缘变形
- 星空看起来更自然

## 修复方案

### 1. 修复传感器数据转换

```typescript
// src/core/Tensors/sensor.ts

// 新的正确公式
if (isIOS) {
    azimuth = data.alpha  // 指南针方向保持不变
    altitude = data.beta - 90  // 关键修复！
    
    // 现在的行为：
    // 手机平躺朝上(beta=-90) → altitude=0，然后调整为90(天顶)
    // 手机竖直(beta=0) → altitude=-90，然后调整为0(地平线)
}
```

### 2. 修复相机 lookAt

```typescript
// src/core/renderer/GroundObserverRenderer.ts

private updateCameraFromSensor(): void {
    const { azimuth, altitude } = this.cameraOrientation;
    
    // 计算远处的目标点（关键！）
    const distance = this.SKY_RADIUS;  // 1000
    const target = new THREE.Vector3(
        Math.sin(azimuthRad) * Math.cos(altitudeRad) * distance,
        Math.sin(altitudeRad) * distance,
        Math.cos(azimuthRad) * Math.cos(altitudeRad) * distance
    );
    
    // 相机始终在原点，看向远处的目标点
    this.camera.position.set(0, 0, 0);
    this.camera.lookAt(target);
    this.camera.updateProjectionMatrix();
}
```

### 3. 调整相机参数

```typescript
// 减小FOV，减少变形
this.camera = new THREE.PerspectiveCamera(
    60,  // 从75降到60
    width / height,
    0.1,
    SKY_RADIUS * 2
);

// 初始朝向天顶
this.camera.lookAt(0, 1, 0);
```

## 效果对比

### 修复前
```
用户动作：手机向上仰，看天空
传感器：beta = -45°
计算：altitude = -(-45) = 45°
结果：✅ 看到星空（但lookAt错误导致变形）

用户动作：手机向下俯，看地面  
传感器：beta = 45°
计算：altitude = -(45) = -45°
结果：看到地面（正确但无用）

问题：虽然方向对了，但lookAt使用错误
```

### 修复后
```
用户动作：手机向上仰，看天空
传感器：beta = -45°
计算：altitude = -45 - 90 = -135 → 归一化 45°
目标点：(sin(az)*cos(45)*1000, sin(45)*1000, cos(az)*cos(45)*1000)
结果：✅ 正确看到45°仰角的星空

用户动作：手机竖直握持
传感器：beta = 0°
计算：altitude = 0 - 90 = -90 → 归一化 0°
目标点：(sin(az)*1000, 0, cos(az)*1000)
结果：✅ 正确看到地平线

用户动作：手机平躺朝上（看天顶）
传感器：beta = -90°
计算：altitude = -90 - 90 = -180 → 归一化 90°
目标点：(0, 1000, 0)
结果：✅ 正确看到天顶
```

## 坐标系统说明

### Three.js 坐标系
```
      Y (上)
      |
      |
      +------ X (东)
     /
    /
   Z (南)
```

### 天文坐标转Three.js
```
方位角(Azimuth):
- 0° = 北 → -Z轴方向
- 90° = 东 → +X轴方向  
- 180° = 南 → +Z轴方向
- 270° = 西 → -X轴方向

仰角(Altitude):
- 90° = 天顶 → +Y轴方向
- 0° = 地平线 → XZ平面
- -90° = 天底 → -Y轴方向
```

### 计算公式
```javascript
// 球坐标转笛卡尔坐标
x = sin(azimuth) * cos(altitude) * radius
y = sin(altitude) * radius
z = cos(azimuth) * cos(altitude) * radius
```

## 测试验证

### 测试步骤

1. **手机竖直握持**
   ```
   预期：
   - 仰角 ≈ 0° (地平线)
   - 看到地平线附近的星星
   ```

2. **手机向上仰45度**
   ```
   预期：
   - 仰角 ≈ 45°
   - 看到中等高度的星空
   ```

3. **手机平躺朝上**
   ```
   预期：
   - 仰角 ≈ 90° (天顶)
   - 看到正上方的星空
   - 北极星应该在视野中央（如果在北半球）
   ```

4. **转动手机360度**
   ```
   预期：
   - 方位角从0-360度变化
   - 看到不同方向的星空
   - 星座位置与真实天空一致
   ```

### 预期显示值

当手机向上看天空时：
```
方位角: 0-360° (取决于朝向)
仰角: 30-90° (正值，向上)
```

当手机竖直握持时：
```
方位角: 0-360° (取决于朝向)
仰角: 0° 左右 (地平线)
```

## 常见问题

### Q: 为什么需要减90？

A: 因为iOS的beta定义是：
- 0° = 竖直握持
- -90° = 平躺朝上（看天空）

而天文学的altitude定义是：
- 0° = 地平线（水平看）
- 90° = 天顶（垂直向上看）

所以需要转换：`altitude = beta - 90`

### Q: 为什么不能用单位向量？

A: `lookAt` 方法的工作原理是：
1. 计算从相机位置到目标点的方向
2. 设置相机朝向这个方向

如果目标点太近（如单位向量），会导致：
- 视角计算错误
- 投影矩阵失真
- 边缘严重变形

### Q: 星星还是有点变形怎么办？

A: 可以进一步调整：
```javascript
// 减小FOV（更窄的视角）
FOV: 50-55° 

// 或增加near plane
near: 1.0 (而不是0.1)
```

## 性能优化

### 避免频繁的矩阵更新
```javascript
// 只在传感器数据变化时更新
if (orientationChanged) {
    this.camera.lookAt(target);
    this.camera.updateProjectionMatrix();
}
```

### 限制更新频率
```javascript
// 使用节流，每16ms更新一次
const throttledUpdate = throttle(
    updateCameraFromSensor, 
    16
);
```

## 调试技巧

### 在控制台查看传感器数据
```javascript
console.log('传感器数据:', {
    alpha: data.alpha,
    beta: data.beta,
    gamma: data.gamma
});

console.log('计算结果:', {
    azimuth: azimuth,
    altitude: altitude
});

console.log('相机朝向:', {
    target: target,
    position: camera.position
});
```

### 添加辅助线
```javascript
// 添加坐标轴辅助线（开发时）
const axesHelper = new THREE.AxesHelper(100);
scene.add(axesHelper);

// 添加网格辅助线
const gridHelper = new THREE.GridHelper(2000, 20);
scene.add(gridHelper);
```

---

**现在刷新页面测试：**

1. ✅ 手机向上仰应该看到星空
2. ✅ 手机竖直握持应该看到地平线
3. ✅ 星星不应该变形
4. ✅ 转动手机星空应该跟随

如果仍有问题，请：
- 截图显示仰角数值
- 说明手机握持姿势
- 描述看到的效果
