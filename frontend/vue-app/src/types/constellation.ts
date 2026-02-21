// 星座形状枚举
export type ConstellationShapeId = 'bird' | 'lion' | 'human' | 'scorpion' | 'bear' | 'cross' | 'triangle' | 'generic';

// 星点数据接口
export interface StarData {
    id: number;
    hip?: number; // Hipparcos 编号
    ra: number; // 赤经 (Right Ascension) 0~360度 或 0~24h
    dec: number; // 赤纬 (Declination) -90~+90度
    mag: number; // 视星等 (Magnitude)
    color?: string; // 光谱颜色
}

// 星座基础数据
export interface ConstellationData {
    id: string; // 缩写，如 ORI (猎户)
    name: {
        en: string; // Orion
        zh: string; // 猎户座
    };
    description?: string;
    shapeId: ConstellationShapeId; // 对应的 3D 形状 ID
    center: { ra: number; dec: number }; // 星座中心点，用于放置模型
    stars: StarData[]; // 星座包含的主要亮星
    lines: number[][]; // 连线索引对，例如 [[0, 1], [1, 2]] 代表 stars[0] 连 stars[1]
}

