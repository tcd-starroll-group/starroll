import * as THREE from 'three';

/**
 * 坐标转换工具
 * 核心任务：将天球坐标 (RA, Dec) 映射到 3D 笛卡尔坐标 (x, y, z)
 */
export class AstroCoordinates {
    
    /**
     * 将赤道坐标转换为单位球面的笛卡尔坐标
     * @param ra 赤经 (Right Ascension) - 单位：度 (0~360)
     * @param dec 赤纬 (Declination) - 单位：度 (-90~+90)
     * @param radius 半径 (默认 1)
     */
    public static raDecToVector3(ra: number, dec: number, radius: number = 1000): THREE.Vector3 {
        // 1. 角度转弧度
        // RA 通常逆时针增加，Three.js 中可能需要取反来匹配天空盒方向
        // 这里假设：Z轴指北极，X轴指春分点
        
        const phi = THREE.MathUtils.degToRad(90 - dec); // 极角 (从北极向下)
        const theta = THREE.MathUtils.degToRad(ra);     // 方位角 (RA)

        // 球坐标转笛卡尔坐标
        // x = r * sin(phi) * cos(theta)
        // z = r * sin(phi) * sin(theta)  <-- 注意 Three.js Y 是上，这里我们暂时假设 Y 是北极
        // y = r * cos(phi)
        
        // 修正：在 Three.js 中，通常 Y 是 Up (北极)，X/Z 是赤道平面
        // x = r * cos(dec) * cos(ra)
        // z = r * cos(dec) * sin(ra)  (或者反过来，取决于坐标系手性)
        // y = r * sin(dec)
        
        const decRad = THREE.MathUtils.degToRad(dec);
        const raRad = THREE.MathUtils.degToRad(ra);

        const x = radius * Math.cos(decRad) * Math.cos(raRad);
        const z = -radius * Math.cos(decRad) * Math.sin(raRad); // 翻转 Z 以匹配右手坐标系惯例
        const y = radius * Math.sin(decRad);

        return new THREE.Vector3(x, y, z);
    }
}

