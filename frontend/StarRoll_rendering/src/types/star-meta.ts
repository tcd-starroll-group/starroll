/**
 * 星表数据类型定义
 */

export interface EquatorialCoordinate {
  rightAscension: number  // 赤经 (度)
  declination: number     // 赤纬 (度)
}

export interface StarMeta {
  hIP: number                              // HIP 编号
  equatorialCoordinate: EquatorialCoordinate
  magnitude: number                        // 视星等
  pmRA: number                             // 赤经自行
  pmDE: number                             // 赤纬自行
  bvColor: number                          // B-V 色指数
  distance?: number                        // 距离（光年）
}

/**
 * 星座连线定义
 */
export interface ConstellationLines {
  id: string           // 星座 ID (如 'ORI', 'CYG')
  name: string         // 星座名称
  lines: number[][]    // 连线定义，每对数字是两个 HIP 编号
}
