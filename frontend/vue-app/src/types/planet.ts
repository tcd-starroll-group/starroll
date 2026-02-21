export interface PlanetConfig {
    id: string;
    name: string; // 中文名称
    type: 'star' | 'planet' | 'dwarf'; // 类型：恒星、行星、矮行星
    radius: number; // 行星半径 (相对于地球或自定义单位)
    orbitRadius: number; // 轨道半径 (距离太阳的距离)
    orbitPeriod: number; // 公转周期 (例如：地球=1)
    rotationPeriod: number; // 自转周期
    color: string | number; // 基础色
    textureUrl?: string; // (可选) 贴图路径
    
    // 光环配置
    hasRings?: boolean;
    ringConfig?: {
        innerRadius: number;
        outerRadius: number;
        color: string | number;
        count?: number; // 粒子数量
    };

    // 视觉配置
    visual?: {
        emissive?: boolean; // 是否自发光 (太阳)
        roughness?: number; // 粗糙度
        metalness?: number; // 金属度
        // 噪声纹理控制
        noiseScale?: number;    // 噪声的密度
        noiseStrength?: number; // 噪声对颜色的干扰强度
        rimPower?: number;      // 边缘光强度
    };
}
