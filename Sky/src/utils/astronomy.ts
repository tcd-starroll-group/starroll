
export function getCartesianPosition(ra: number, dec: number, radius: number = 500): { x: number, y: number, z: number } {
  // Convert RA (hours) to degrees: 1h = 15deg
  const raRad = (ra * 15) * (Math.PI / 180);
  
  // In Three.js/A-Frame: Y is Up.
  // Conventionally: Dec maps to pitch (Y axis component), RA maps to yaw (X/Z plane)
  const phi = (90 - dec) * (Math.PI / 180); // Polar angle (from top)
  const theta = raRad; // Azimuthal angle

  const x = -(radius * Math.sin(phi) * Math.cos(theta));
  const y = radius * Math.cos(phi);
  const z = -(radius * Math.sin(phi) * Math.sin(theta));

  return { x, y, z };
}
//  把天球坐标转换为笛卡尔坐标系 (Three.js/A-Frame坐标系)
//  ra: 赤经 (小时制)
//  dec: 赤纬 (度制)
//  radius: 半径 (默认500)

//  返回值: { x, y, z } 笛卡尔坐标系位置 代码对坐标做了符合调整来匹配渲染坐标系