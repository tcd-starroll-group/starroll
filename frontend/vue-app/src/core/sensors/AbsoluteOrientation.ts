export interface AbsoluteOrientationData {
  quaternion: [number, number, number, number]; // 四元数数据
}

export type SensorCallback = (data: AbsoluteOrientationData) => void;

class AbsoluteOrientationManager {
  private listeners: Set<SensorCallback> = new Set();
  private isListening: boolean = false;
  private permissionState: PermissionState = "prompt";
  private lastData: AbsoluteOrientationData | null = null;
  private sensor: AbsoluteOrientationSensor | null = null;

  startListening(): void {
    if (this.isListening) {
      console.warn("传感器已在监听中");
      return;
    }

    this.sensor = new AbsoluteOrientationSensor({ frequency: 60 });

    this.sensor.addEventListener("reading", () => {
      const quaternion = this.sensor?.quaternion as [
        number,
        number,
        number,
        number,
      ];
      const data: AbsoluteOrientationData = {
        quaternion,
      };

      this.lastData = data;
      this.listeners.forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error("传感器回调函数执行失败:", error);
        }
      });
    });

    this.sensor.addEventListener("error", (event) => {
      console.error("传感器错误:", event.error);
    });

    this.sensor.start();
    this.isListening = true;
    console.log("📡 开始监听 AbsoluteOrientationSensor 数据");
  }

  stopListening(): void {
    if (!this.isListening || !this.sensor) {
      return;
    }

    this.sensor.stop();
    this.sensor = null;
    this.isListening = false;
    console.log("🛑 停止监听 AbsoluteOrientationSensor 数据");
  }

  addListener(callback: SensorCallback): void {
    this.listeners.add(callback);
  }

  getLastData(): AbsoluteOrientationData | null {
    return this.lastData;
  }
}

// 导出单例实例
export const absoluteOrientationManager = new AbsoluteOrientationManager();

// 导出类以便测试
export { AbsoluteOrientationManager };
