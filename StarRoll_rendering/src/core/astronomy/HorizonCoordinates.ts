import * as THREE from 'three';

/**
 * 地平坐标系转换
 * 将赤道坐标转换为地平坐标（考虑观测者位置和时间）
 */
export class HorizonCoordinates {
    
    /**
     * 将赤道坐标转换为地平坐标
     * @param ra 赤经（度）
     * @param dec 赤纬（度）
     * @param latitude 观测者纬度（度）
     * @param longitude 观测者经度（度）
     * @param localSiderealTime 本地恒星时（度）
     * @returns { altitude, azimuth } 高度角和方位角
     */
    public static equatorialToHorizon(
        ra: number,
        dec: number,
        latitude: number,
        localSiderealTime: number
    ): { altitude: number, azimuth: number } {
        // 计算时角（Hour Angle）
        const hourAngle = localSiderealTime - ra;
        
        // 转换为弧度
        const haRad = THREE.MathUtils.degToRad(hourAngle);
        const decRad = THREE.MathUtils.degToRad(dec);
        const latRad = THREE.MathUtils.degToRad(latitude);
        
        // 计算高度角（Altitude）
        const sinAlt = Math.sin(decRad) * Math.sin(latRad) + 
                       Math.cos(decRad) * Math.cos(latRad) * Math.cos(haRad);
        const altitude = Math.asin(sinAlt);
        
        // 计算方位角（Azimuth）
        const cosAz = (Math.sin(decRad) - Math.sin(altitude) * Math.sin(latRad)) / 
                      (Math.cos(altitude) * Math.cos(latRad));
        let azimuth = Math.acos(Math.max(-1, Math.min(1, cosAz)));
        
        // 修正方位角象限
        if (Math.sin(haRad) > 0) {
            azimuth = 2 * Math.PI - azimuth;
        }
        
        return {
            altitude: THREE.MathUtils.radToDeg(altitude),
            azimuth: THREE.MathUtils.radToDeg(azimuth)
        };
    }
    
    /**
     * 地平坐标转 3D 位置（以观测者为中心）
     * @param altitude 高度角（度，0=地平线，90=天顶）
     * @param azimuth 方位角（度，0=北，90=东，180=南，270=西）
     * @param radius 距离
     */
    public static horizonToVector3(
        altitude: number,
        azimuth: number,
        radius: number
    ): THREE.Vector3 {
        const altRad = THREE.MathUtils.degToRad(altitude);
        const azRad = THREE.MathUtils.degToRad(azimuth);
        
        // 地平坐标系：
        // Y 轴向上（天顶）
        // X 轴向东
        // Z 轴向北
        
        const x = radius * Math.cos(altRad) * Math.sin(azRad);
        const y = radius * Math.sin(altRad);
        const z = radius * Math.cos(altRad) * Math.cos(azRad);
        
        return new THREE.Vector3(x, y, z);
    }
    
    /**
     * 计算本地恒星时（简化版本）
     * @param longitude 经度（度）
     * @param date 日期时间
     */
    public static calculateLocalSiderealTime(
        longitude: number,
        date: Date = new Date()
    ): number {
        // 简化计算（实际应该考虑儒略日等）
        const hours = date.getUTCHours() + date.getUTCMinutes() / 60;
        const lst = (hours * 15 + longitude) % 360;
        return lst;
    }
}

/**
 * 观测者配置
 */
export interface ObserverLocation {
    latitude: number;   // 纬度（度，-90 到 90）
    longitude: number;  // 经度（度，-180 到 180）
    name?: string;      // 地点名称
}

/**
 * 常用观测地点
 */
export const OBSERVER_LOCATIONS = {
    // 中国主要城市
    BEIJING: { latitude: 39.9, longitude: 116.4, name: '北京' },
    SHANGHAI: { latitude: 31.2, longitude: 121.5, name: '上海' },
    GUANGZHOU: { latitude: 23.1, longitude: 113.3, name: '广州' },
    
    // 其他地点
    NEW_YORK: { latitude: 40.7, longitude: -74.0, name: 'New York' },
    LONDON: { latitude: 51.5, longitude: -0.1, name: 'London' },
    TOKYO: { latitude: 35.7, longitude: 139.7, name: 'Tokyo' }
};
