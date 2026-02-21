import * as THREE from 'three'

/**
 * 将赤道坐标 (RA, Dec) 转换为 3D 笛卡尔坐标
 * @param ra 赤经 (度)
 * @param dec 赤纬 (度)
 * @param radius 半径，默认 1000
 */
export function raDecToVector3(ra: number, dec: number, radius: number = 1000): THREE.Vector3 {
  const decRad = THREE.MathUtils.degToRad(dec)
  const raRad = THREE.MathUtils.degToRad(ra)

  const x = radius * Math.cos(decRad) * Math.cos(raRad)
  const z = -radius * Math.cos(decRad) * Math.sin(raRad) // 翻转 Z 以匹配右手坐标系惯例
  const y = radius * Math.sin(decRad)

  return new THREE.Vector3(x, y, z)
}
