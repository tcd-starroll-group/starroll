import * as THREE from 'three'

/**
 * 将赤道坐标 (RA, Dec) 转换为 3D 笛卡尔坐标
 * three.js 使用右手坐标系 +X 向右，+Y 向上，+Z 指向观察者
 * @param ra 赤经 (度)
 * @param dec 赤纬 (度)
 * @param radius 半径，默认 1000
 */
export function raDecToVector3(ra: number, dec: number, radius: number = 1000): THREE.Vector3 {
  const decRad = THREE.MathUtils.degToRad(dec)
  // 这里将星星绕y轴旋转90度，以对其手机的初始方向。这里是减，因为raRad是向东为正。
  const raRad = THREE.MathUtils.degToRad(ra) - Math.PI / 2

  const x = radius * Math.cos(decRad) * Math.cos(raRad)
  const z = -radius * Math.cos(decRad) * Math.sin(raRad) // because raRad increases clockwise
  const y = radius * Math.sin(decRad)

  return new THREE.Vector3(x, y, z)
}
