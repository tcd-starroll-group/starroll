import * as THREE from 'three';

// 使用 AFRAME 的 THREE 实例
export function createConstellationShape(constellationId: string, THREE: any): THREE.Group {
  const group = new THREE.Group();

  switch (constellationId) {
    case 'aries':
      return createRam(THREE);
    case 'taurus':
      return createBull(THREE);
    case 'gemini':
      return createTwins(THREE);
    case 'cancer':
      return createCrab(THREE);
    case 'leo':
      return createLion(THREE);
    case 'virgo':
      return createVirgin(THREE);
    case 'libra':
      return createScales(THREE);
    case 'scorpio':
      return createScorpion(THREE);
    case 'sagittarius':
      return createArcher(THREE);
    case 'capricorn':
      return createGoat(THREE);
    case 'aquarius':
      return createWaterBearer(THREE);
    case 'pisces':
      return createFish(THREE);
    default:
      return group;
  }
}

// 增强的发光材质（更亮）
function getGlowMaterial(THREE: any, color: number, opacity: number = 0.8) {
  return new THREE.MeshBasicMaterial({
    color,
    transparent: true,
    opacity,
    side: THREE.DoubleSide,
    blending: THREE.AdditiveBlending
  });
}

// 创建粒子光环
function createParticleHalo(THREE: any, color: number, count: number = 100, radius: number = 20): THREE.Points {
  const geometry = new THREE.BufferGeometry();
  const positions = [];
  
  for (let i = 0; i < count; i++) {
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.random() * Math.PI;
    const r = radius * (0.8 + Math.random() * 0.4);
    
    positions.push(
      r * Math.sin(phi) * Math.cos(theta),
      r * Math.sin(phi) * Math.sin(theta),
      r * Math.cos(phi)
    );
  }
  
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  
  const material = new THREE.PointsMaterial({
    color,
    size: 0.8,
    transparent: true,
    opacity: 0.8,
    blending: THREE.AdditiveBlending
  });
  
  return new THREE.Points(geometry, material);
}

// 1. 白羊座 - 增强版
function createRam(THREE: any): THREE.Group {
  const group = new THREE.Group();
  
  // 粒子光环
  const halo = createParticleHalo(THREE, 0xffaa88, 150, 25);
  group.add(halo);
  
  // 发光核心
  const coreGeo = new THREE.SphereGeometry(10, 32, 32);
  const core = new THREE.Mesh(coreGeo, getGlowMaterial(THREE, 0xffcc88, 0.9));
  group.add(core);
  
  // 头部（更亮）
  const headGeo = new THREE.SphereGeometry(8, 16, 16);
  const head = new THREE.Mesh(headGeo, getGlowMaterial(THREE, 0xffaa88, 0.7));
  group.add(head);
  
  // 金色螺旋角（加粗）
  const hornCurve1 = new THREE.CatmullRomCurve3([
    new THREE.Vector3(-5, 3, 0),
    new THREE.Vector3(-8, 8, -3),
    new THREE.Vector3(-10, 10, -5),
    new THREE.Vector3(-8, 12, -3)
  ]);
  const hornGeo1 = new THREE.TubeGeometry(hornCurve1, 20, 1.5, 8, false);
  const horn1 = new THREE.Mesh(hornGeo1, getGlowMaterial(THREE, 0xffd700, 0.9));
  group.add(horn1);
  
  const hornCurve2 = new THREE.CatmullRomCurve3([
    new THREE.Vector3(5, 3, 0),
    new THREE.Vector3(8, 8, -3),
    new THREE.Vector3(10, 10, -5),
    new THREE.Vector3(8, 12, -3)
  ]);
  const hornGeo2 = new THREE.TubeGeometry(hornCurve2, 20, 1.5, 8, false);
  const horn2 = new THREE.Mesh(hornGeo2, getGlowMaterial(THREE, 0xffd700, 0.9));
  group.add(horn2);
  
  return group;
}

// 2. 金牛座 - 增强版
function createBull(THREE: any): THREE.Group {
  const group = new THREE.Group();
  
  // 粒子云
  const particles = createParticleHalo(THREE, 0xff8844, 200, 30);
  group.add(particles);
  
  // 发光核心
  const coreGeo = new THREE.SphereGeometry(8, 32, 32);
  const core = new THREE.Mesh(coreGeo, getGlowMaterial(THREE, 0xffaa66, 0.8));
  group.add(core);
  
  // 牛头
  const headGeo = new THREE.BoxGeometry(12, 10, 8);
  const head = new THREE.Mesh(headGeo, getGlowMaterial(THREE, 0xff8844, 0.7));
  group.add(head);
  
  // 强化牛角
  const horn1Geo = new THREE.ConeGeometry(2, 18, 8);
  const horn1 = new THREE.Mesh(horn1Geo, getGlowMaterial(THREE, 0xffffaa, 0.9));
  horn1.position.set(-8, 10, 0);
  horn1.rotation.z = -Math.PI / 6;
  group.add(horn1);
  
  const horn2 = horn1.clone();
  horn2.position.set(8, 10, 0);
  horn2.rotation.z = Math.PI / 6;
  group.add(horn2);
  
  return group;
}

// 3. 双子座 - 增强版
function createTwins(THREE: any): THREE.Group {
  const group = new THREE.Group();
  
  const createHumanoid = (xOffset: number) => {
    const human = new THREE.Group();
    
    // 发光光环
    const halo = createParticleHalo(THREE, 0xaaddff, 80, 15);
    human.add(halo);
    
    // 头部（发光）
    const headGeo = new THREE.SphereGeometry(3, 16, 16);
    const head = new THREE.Mesh(headGeo, getGlowMaterial(THREE, 0xccddff, 0.9));
    head.position.y = 10;
    human.add(head);
    
    // 身体
    const bodyGeo = new THREE.CylinderGeometry(2, 3, 12, 8);
    const body = new THREE.Mesh(bodyGeo, getGlowMaterial(THREE, 0x88ccff, 0.7));
    human.add(body);
    
    // 发光手臂
    const armGeo = new THREE.CylinderGeometry(0.8, 0.8, 8, 6);
    const arm1 = new THREE.Mesh(armGeo, getGlowMaterial(THREE, 0xaaddff, 0.7));
    arm1.position.set(-4, 2, 0);
    arm1.rotation.z = Math.PI / 4;
    human.add(arm1);
    
    const arm2 = arm1.clone();
    arm2.position.x = 4;
    arm2.rotation.z = -Math.PI / 4;
    human.add(arm2);
    
    human.position.x = xOffset;
    return human;
  };
  
  // 连接能量线
  const linkGeo = new THREE.BufferGeometry();
  linkGeo.setAttribute('position', new THREE.Float32BufferAttribute([
    -8, 0, 0, 8, 0, 0
  ], 3));
  const link = new THREE.Line(linkGeo, new THREE.LineBasicMaterial({ 
    color: 0xaaddff, 
    opacity: 0.8, 
    transparent: true,
    linewidth: 3
  }));
  group.add(link);
  
  group.add(createHumanoid(-8));
  group.add(createHumanoid(8));
  
  return group;
}

// 4. 巨蟹座 - 增强版
function createCrab(THREE: any): THREE.Group {
  const group = new THREE.Group();
  
  // 粒子云
  const particles = createParticleHalo(THREE, 0xff6666, 180, 28);
  group.add(particles);
  
  // 发光核心
  const coreGeo = new THREE.SphereGeometry(9, 32, 32);
  coreGeo.scale(1.5, 0.8, 1);
  const core = new THREE.Mesh(coreGeo, getGlowMaterial(THREE, 0xff8888, 0.8));
  group.add(core);
  
  // 身体
  const bodyGeo = new THREE.SphereGeometry(6, 16, 16);
  bodyGeo.scale(1.5, 0.8, 1);
  const body = new THREE.Mesh(bodyGeo, getGlowMaterial(THREE, 0xff6666, 0.6));
  group.add(body);
  
  // 发光的腿
  for (let i = 0; i < 4; i++) {
    const legCurve = new THREE.QuadraticBezierCurve3(
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(8, -5, 0),
      new THREE.Vector3(12, -8, 0)
    );
    const legGeo = new THREE.TubeGeometry(legCurve, 10, 0.8, 6, false);
    const leg = new THREE.Mesh(legGeo, getGlowMaterial(THREE, 0xff8888, 0.7));
    
    const angle = (i / 4) * Math.PI;
    leg.rotation.y = angle;
    leg.position.x = Math.cos(angle) * 5;
    leg.position.z = Math.sin(angle) * 5;
    group.add(leg);
    
    const leg2 = leg.clone();
    leg2.rotation.y = -angle;
    leg2.position.x = Math.cos(-angle) * 5;
    leg2.position.z = Math.sin(-angle) * 5;
    group.add(leg2);
  }
  
  // 发光钳子
  const clawGeo = new THREE.SphereGeometry(4, 16, 16);
  const claw1 = new THREE.Mesh(clawGeo, getGlowMaterial(THREE, 0xff4444, 0.9));
  claw1.position.set(-10, 2, 0);
  group.add(claw1);
  
  const claw2 = claw1.clone();
  claw2.position.x = 10;
  group.add(claw2);
  
  return group;
}

// 5. 狮子座 - 增强版
function createLion(THREE: any): THREE.Group {
  const group = new THREE.Group();
  
  // 强烈的金色粒子云
  const particles = createParticleHalo(THREE, 0xffaa00, 250, 35);
  group.add(particles);
  
  // 发光核心
  const coreGeo = new THREE.SphereGeometry(12, 32, 32);
  const core = new THREE.Mesh(coreGeo, getGlowMaterial(THREE, 0xffcc00, 0.9));
  group.add(core);
  
  // 头部
  const headGeo = new THREE.SphereGeometry(7, 16, 16);
  const head = new THREE.Mesh(headGeo, getGlowMaterial(THREE, 0xffaa00, 0.8));
  group.add(head);
  
  // 放射状发光鬃毛
  const maneGeo = new THREE.ConeGeometry(3, 12, 4);
  for (let i = 0; i < 16; i++) {
    const angle = (i / 16) * Math.PI * 2;
    const mane = new THREE.Mesh(maneGeo, getGlowMaterial(THREE, 0xffcc00, 0.8));
    mane.position.x = Math.cos(angle) * 12;
    mane.position.y = Math.sin(angle) * 12;
    mane.lookAt(0, 0, 0);
    group.add(mane);
  }
  
  return group;
}

// 6-12. 其他星座（类似增强，添加粒子和发光效果）
function createVirgin(THREE: any): THREE.Group {
  const group = new THREE.Group();
  const particles = createParticleHalo(THREE, 0xffddee, 120, 25);
  group.add(particles);
  
  const coreGeo = new THREE.SphereGeometry(6, 32, 32);
  const core = new THREE.Mesh(coreGeo, getGlowMaterial(THREE, 0xffeeff, 0.8));
  group.add(core);
  
  const headGeo = new THREE.SphereGeometry(4, 16, 16);
  const head = new THREE.Mesh(headGeo, getGlowMaterial(THREE, 0xffddee, 0.8));
  head.position.y = 12;
  group.add(head);
  
  const bodyGeo = new THREE.CylinderGeometry(2, 8, 15, 16);
  const body = new THREE.Mesh(bodyGeo, getGlowMaterial(THREE, 0xddbbff, 0.7));
  group.add(body);
  
  return group;
}

function createScales(THREE: any): THREE.Group {
  const group = new THREE.Group();
  const particles = createParticleHalo(THREE, 0xaaccff, 150, 30);
  group.add(particles);
  
  const poleGeo = new THREE.CylinderGeometry(0.8, 0.8, 20, 8);
  const pole = new THREE.Mesh(poleGeo, getGlowMaterial(THREE, 0xccddff, 0.9));
  group.add(pole);
  
  const beamGeo = new THREE.CylinderGeometry(0.8, 0.8, 30, 8);
  const beam = new THREE.Mesh(beamGeo, getGlowMaterial(THREE, 0xaaccff, 0.9));
  beam.rotation.z = Math.PI / 2;
  beam.position.y = 8;
  group.add(beam);
  
  const plateGeo = new THREE.CylinderGeometry(5, 5, 1, 16);
  const plate1 = new THREE.Mesh(plateGeo, getGlowMaterial(THREE, 0x88ddff, 0.7));
  plate1.position.set(-12, 0, 0);
  group.add(plate1);
  
  const plate2 = plate1.clone();
  plate2.position.x = 12;
  group.add(plate2);
  
  return group;
}

function createScorpion(THREE: any): THREE.Group {
  const group = new THREE.Group();
  const particles = createParticleHalo(THREE, 0xff3333, 200, 32);
  group.add(particles);
  
  for (let i = 0; i < 5; i++) {
    const segmentGeo = new THREE.SphereGeometry(3.5 - i * 0.3, 16, 16);
    const segment = new THREE.Mesh(segmentGeo, getGlowMaterial(THREE, 0xff3333, 0.8));
    segment.position.z = -i * 4;
    group.add(segment);
  }
  
  const tailCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0, -20),
    new THREE.Vector3(0, 5, -25),
    new THREE.Vector3(0, 12, -28),
    new THREE.Vector3(0, 15, -25)
  ]);
  const tailGeo = new THREE.TubeGeometry(tailCurve, 20, 1.5, 8, false);
  const tail = new THREE.Mesh(tailGeo, getGlowMaterial(THREE, 0xff6666, 0.9));
  group.add(tail);
  
  const clawGeo = new THREE.SphereGeometry(5, 16, 16);
  clawGeo.scale(1.5, 0.8, 0.8);
  const claw1 = new THREE.Mesh(clawGeo, getGlowMaterial(THREE, 0xff4444, 0.9));
  claw1.position.set(-6, 0, 5);
  group.add(claw1);
  
  const claw2 = claw1.clone();
  claw2.position.x = 6;
  group.add(claw2);
  
  return group;
}

function createArcher(THREE: any): THREE.Group {
  const group = new THREE.Group();
  const particles = createParticleHalo(THREE, 0xffaa00, 160, 28);
  group.add(particles);
  
  const bowCurve = new THREE.QuadraticBezierCurve3(
    new THREE.Vector3(-8, -10, 0),
    new THREE.Vector3(-12, 0, 0),
    new THREE.Vector3(-8, 10, 0)
  );
  const bowGeo = new THREE.TubeGeometry(bowCurve, 20, 1, 8, false);
  const bow = new THREE.Mesh(bowGeo, getGlowMaterial(THREE, 0xffaa00, 0.9));
  group.add(bow);
  
  const arrowGeo = new THREE.CylinderGeometry(0.5, 0.5, 20, 8);
  const arrow = new THREE.Mesh(arrowGeo, getGlowMaterial(THREE, 0xffddaa, 0.9));
  arrow.rotation.z = Math.PI / 2;
  arrow.position.x = 5;
  group.add(arrow);
  
  const tipGeo = new THREE.ConeGeometry(1.5, 4, 6);
  const tip = new THREE.Mesh(tipGeo, getGlowMaterial(THREE, 0xffdd00, 1.0));
  tip.rotation.z = -Math.PI / 2;
  tip.position.x = 15;
  group.add(tip);
  
  return group;
}

function createGoat(THREE: any): THREE.Group {
  const group = new THREE.Group();
  const particles = createParticleHalo(THREE, 0x88aa66, 140, 26);
  group.add(particles);
  
  const headGeo = new THREE.SphereGeometry(5, 16, 16);
  const head = new THREE.Mesh(headGeo, getGlowMaterial(THREE, 0xaabb88, 0.8));
  head.position.y = 8;
  group.add(head);
  
  const hornGeo = new THREE.ConeGeometry(1.5, 10, 6);
  const horn1 = new THREE.Mesh(hornGeo, getGlowMaterial(THREE, 0xccdd99, 0.9));
  horn1.position.set(-3, 12, 0);
  horn1.rotation.z = -Math.PI / 6;
  group.add(horn1);
  
  const horn2 = horn1.clone();
  horn2.position.x = 3;
  horn2.rotation.z = Math.PI / 6;
  group.add(horn2);
  
  const bodyGeo = new THREE.CylinderGeometry(4, 2, 10, 16);
  const body = new THREE.Mesh(bodyGeo, getGlowMaterial(THREE, 0x88aa77, 0.7));
  group.add(body);
  
  const tailGeo = new THREE.ConeGeometry(5, 14, 4);
  const tail = new THREE.Mesh(tailGeo, getGlowMaterial(THREE, 0x66aaaa, 0.8));
  tail.position.y = -12;
  tail.rotation.y = Math.PI / 4;
  group.add(tail);
  
  return group;
}

function createWaterBearer(THREE: any): THREE.Group {
  const group = new THREE.Group();
  const particles = createParticleHalo(THREE, 0x44aaff, 180, 30);
  group.add(particles);
  
  const jarGeo = new THREE.CylinderGeometry(5, 7, 15, 16);
  const jar = new THREE.Mesh(jarGeo, getGlowMaterial(THREE, 0x66ccff, 0.8));
  jar.rotation.z = Math.PI / 6;
  jar.position.y = 5;
  group.add(jar);
  
  // 流动的水粒子（更多）
  const waterGeo = new THREE.BufferGeometry();
  const waterPositions = [];
  for (let i = 0; i < 100; i++) {
    waterPositions.push(
      5 + Math.random() * 3,
      15 - i * 0.4,
      (Math.random() - 0.5) * 3
    );
  }
  waterGeo.setAttribute('position', new THREE.Float32BufferAttribute(waterPositions, 3));
  const waterMat = new THREE.PointsMaterial({ 
    color: 0x00ddff, 
    size: 1.0, 
    transparent: true, 
    opacity: 0.9,
    blending: THREE.AdditiveBlending
  });
  const water = new THREE.Points(waterGeo, waterMat);
  group.add(water);
  
  return group;
}

function createFish(THREE: any): THREE.Group {
  const group = new THREE.Group();
  const particles = createParticleHalo(THREE, 0x66bbff, 170, 32);
  group.add(particles);
  
  const createFishShape = (xOffset: number, flipX: number) => {
    const fish = new THREE.Group();
    
    const bodyGeo = new THREE.SphereGeometry(5, 16, 16);
    bodyGeo.scale(2, 1, 0.8);
    const body = new THREE.Mesh(bodyGeo, getGlowMaterial(THREE, 0x66bbff, 0.8));
    fish.add(body);
    
    const tailGeo = new THREE.ConeGeometry(4, 8, 4);
    const tail = new THREE.Mesh(tailGeo, getGlowMaterial(THREE, 0x88ccff, 0.8));
    tail.rotation.z = Math.PI / 2 * flipX;
    tail.position.x = -10 * flipX;
    fish.add(tail);
    
    fish.position.x = xOffset;
    return fish;
  };
  
  group.add(createFishShape(-8, 1));
  group.add(createFishShape(8, -1));
  
  const lineGeo = new THREE.BufferGeometry();
  lineGeo.setAttribute('position', new THREE.Float32BufferAttribute([
    -8, 0, 0, 8, 0, 0
  ], 3));
  const line = new THREE.Line(lineGeo, new THREE.LineBasicMaterial({ 
    color: 0xaaddff, 
    opacity: 0.8, 
    transparent: true,
    linewidth: 2
  }));
  group.add(line);
  
  return group;
}
