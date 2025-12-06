export interface Star {
  ra: number;  // Right Ascension (0-24h)
  dec: number; // Declination (-90 to +90 deg)
  mag: number; // Magnitude (brightness, lower is brighter)
  color?: string; // Spectral color approximation
  name?: string;
}

export interface Constellation {
  id: string;
  name: string;
  latinName: string;
  dates: string;
  element: 'Fire' | 'Earth' | 'Air' | 'Water';
  symbol: string; // Emoji or icon character
  description: string;
  stars: Star[];
  lines: number[][]; // Indices of stars to connect
}

// Helper to generate a star entry
const s = (ra: number, dec: number, mag: number, name?: string, color: string = '#ffffff'): Star => ({ ra, dec, mag, name, color });

export const zodiacData: Constellation[] = [
  {
    id: 'aries',
    name: '白羊座',
    latinName: 'Aries',
    dates: '3.21 - 4.19',
    element: 'Fire',
    symbol: '♈',
    description: '象征新生的开始，充满活力与勇气。',
    stars: [
      s(2.11, 23.5, 2.0, 'Hamal', '#ffddaa'), // Alpha
      s(1.91, 20.8, 2.6, 'Sheratan', '#ffffff'), // Beta
      s(1.89, 19.3, 3.9, 'Mesarthim', '#aaaaff'), // Gamma
      s(2.82, 27.2, 4.6, '41 Ari', '#ccccff'), // Tail
    ],
    lines: [[0, 1], [1, 2], [0, 3]]
  },
  {
    id: 'taurus',
    name: '金牛座',
    latinName: 'Taurus',
    dates: '4.20 - 5.20',
    element: 'Earth',
    symbol: '♉',
    description: '沉稳而坚定，象征着物质与感官的享受。',
    stars: [
      s(4.60, 16.5, 0.85, 'Aldebaran', '#ff4500'), // Alpha (The Bull's Eye)
      s(5.43, 28.6, 1.65, 'Elnath', '#aaddff'), // Beta
      s(3.79, 24.1, 2.9, 'Alcyone', '#ccccff'), // Pleiades
      s(4.33, 15.6, 3.6, 'Hyadum I', '#ffccaa'), 
      s(4.47, 15.9, 3.6, 'Hyadum II', '#ffccaa'),
      s(5.63, 21.1, 3.0, 'Zeta Tau', '#aaddff'), // Horn
    ],
    lines: [[0, 3], [3, 4], [0, 5], [5, 1], [0, 2]]
  },
  {
    id: 'gemini',
    name: '双子座',
    latinName: 'Gemini',
    dates: '5.21 - 6.21',
    element: 'Air',
    symbol: '♊',
    description: '灵动多变，象征着交流与双重性格。',
    stars: [
      s(7.57, 31.9, 1.58, 'Castor', '#ffffff'), // Alpha
      s(7.74, 28.0, 1.14, 'Pollux', '#ffcc99'), // Beta
      s(6.62, 16.4, 1.9, 'Alhena', '#ffffff'), // Gamma
      s(7.33, 21.9, 3.5, 'Wasat', '#ffffcc'), // Delta
      s(6.72, 25.1, 3.0, 'Mebsuta', '#ffffaa'), // Epsilon
    ],
    lines: [[0, 1], [0, 4], [1, 3], [3, 2]]
  },
  {
    id: 'cancer',
    name: '巨蟹座',
    latinName: 'Cancer',
    dates: '6.22 - 7.22',
    element: 'Water',
    symbol: '♋',
    description: '温柔而敏感，象征着家庭与母性光辉。',
    stars: [
      s(8.97, 11.8, 4.2, 'Acubens', '#ffffff'), // Alpha
      s(8.27, 9.2, 3.5, 'Altarf', '#ffcc99'), // Beta
      s(8.72, 21.5, 4.7, 'Asellus Borealis', '#ffffff'), // Gamma
      s(8.74, 18.2, 3.9, 'Asellus Australis', '#ffddaa'), // Delta
    ],
    lines: [[2, 3], [3, 0], [3, 1]]
  },
  {
    id: 'leo',
    name: '狮子座',
    latinName: 'Leo',
    dates: '7.23 - 8.22',
    element: 'Fire',
    symbol: '♌',
    description: '王者风范，象征着自信、尊严与领导力。',
    stars: [
      s(10.13, 11.9, 1.35, 'Regulus', '#aaaaff'), // Alpha
      s(11.81, 14.6, 2.1, 'Denebola', '#ffffff'), // Beta
      s(10.33, 19.8, 2.0, 'Algieba', '#ffcc00'), // Gamma
      s(11.23, 20.5, 2.5, 'Zosma', '#ffffff'), // Delta
    ],
    lines: [[0, 2], [2, 3], [3, 1], [0, 2]]
  },
  {
    id: 'virgo',
    name: '处女座',
    latinName: 'Virgo',
    dates: '8.23 - 9.22',
    element: 'Earth',
    symbol: '♍',
    description: '追求完美，象征着纯洁、秩序与服务。',
    stars: [
      s(13.41, -11.1, 0.98, 'Spica', '#aabbff'), // Alpha
      s(11.84, 1.7, 2.8, 'Zavijava', '#ffffcc'), // Beta
      s(12.69, -1.4, 2.7, 'Porrima', '#ffffaa'), // Gamma
      s(13.03, 10.9, 2.8, 'Vindemiatrix', '#ffcc00'), // Epsilon
    ],
    lines: [[0, 2], [2, 1], [2, 3]]
  },
  {
    id: 'libra',
    name: '天秤座',
    latinName: 'Libra',
    dates: '9.23 - 10.23',
    element: 'Air',
    symbol: '♎',
    description: '和谐与平衡，象征着公正与优雅的人际关系。',
    stars: [
      s(14.84, -16.0, 2.7, 'Zubenelgenubi', '#ffffcc'), // Alpha
      s(15.28, -9.3, 2.6, 'Zubeneschamali', '#aaddff'), // Beta
      s(15.59, -14.7, 3.9, 'Zubenelakrab', '#ffcc99'), // Gamma
    ],
    lines: [[0, 1], [0, 2], [1, 2]]
  },
  {
    id: 'scorpio',
    name: '天蝎座',
    latinName: 'Scorpius',
    dates: '10.24 - 11.22',
    element: 'Water',
    symbol: '♏',
    description: '神秘而深邃，象征着重生、激情与洞察力。',
    stars: [
      s(16.49, -26.4, 1.0, 'Antares', '#ff3300'), // Alpha (Heart)
      s(16.08, -19.8, 2.6, 'Acrab', '#ffffff'), // Beta (Head)
      s(17.56, -37.3, 1.6, 'Shaula', '#aaddff'), // Lambda (Stinger)
      s(16.83, -30.5, 2.3, 'Wei', '#ffccaa'), // Epsilon
      s(16.56, -28.2, 2.9, 'Tau Sco', '#ffffff'),
    ],
    lines: [[1, 0], [0, 4], [4, 3], [3, 2]]
  },
  {
    id: 'sagittarius',
    name: '射手座',
    latinName: 'Sagittarius',
    dates: '11.23 - 12.21',
    element: 'Fire',
    symbol: '♐',
    description: '自由与远方，象征着乐观、智慧与探索精神。',
    stars: [
      s(18.40, -34.3, 1.8, 'Kaus Australis', '#ffffff'), // Epsilon
      s(18.92, -26.2, 2.0, 'Nunki', '#aaddff'), // Sigma
      s(19.04, -29.8, 2.6, 'Ascella', '#ffffff'), // Zeta
      s(18.31, -29.8, 2.7, 'Kaus Media', '#ffcc99'), // Delta
      s(18.46, -25.4, 2.8, 'Kaus Borealis', '#ffcc00'), // Lambda
      s(18.21, -21.0, 3.8, 'Polis', '#ffffff'), // Mu
      s(18.12, -30.4, 2.9, 'Alnasl', '#ffccaa'), // Gamma
    ],
    lines: [[3, 6], [3, 0], [0, 2], [2, 1], [1, 4], [4, 3], [4, 5]]
  },
  {
    id: 'capricorn',
    name: '摩羯座',
    latinName: 'Capricornus',
    dates: '12.22 - 1.19',
    element: 'Earth',
    symbol: '♑',
    description: '坚韧与野心，象征着责任、结构与成就。',
    stars: [
      s(20.29, -12.5, 3.6, 'Algedi', '#ffffcc'), // Alpha
      s(20.35, -14.7, 3.0, 'Dabih', '#ffcc99'), // Beta
      s(21.66, -16.6, 2.8, 'Deneb Algedi', '#ffffff'), // Delta
      s(21.44, -16.1, 3.7, 'Nashira', '#ffffff'), // Gamma
    ],
    lines: [[0, 1], [1, 3], [3, 2]]
  },
  {
    id: 'aquarius',
    name: '水瓶座',
    latinName: 'Aquarius',
    dates: '1.20 - 2.18',
    element: 'Air',
    symbol: '♒',
    description: '革新与人道，象征着独立、创意与未来。',
    stars: [
      s(22.09, -0.3, 2.9, 'Sadalmelik', '#ffffaa'), // Alpha
      s(21.52, -5.5, 2.9, 'Sadalsuud', '#ffffcc'), // Beta
      s(22.35, -1.3, 3.8, 'Sadachbia', '#ffffff'), // Gamma
      s(22.90, -15.8, 3.2, 'Skat', '#ffffff'), // Delta
    ],
    lines: [[1, 0], [0, 2], [2, 3]]
  },
  {
    id: 'pisces',
    name: '双鱼座',
    latinName: 'Pisces',
    dates: '2.19 - 3.20',
    element: 'Water',
    symbol: '♓',
    description: '梦幻与包容，象征着直觉、艺术与无私的爱。',
    stars: [
      s(2.03, 2.7, 3.8, 'Alrescha', '#ffffff'), // Alpha
      s(23.99, -6.0, 4.5, 'Fum al Samakah', '#ffffff'), // Beta
      s(23.28, 3.2, 3.7, 'Gamma Psc', '#ffffaa'), // Gamma
      s(0.81, 7.5, 4.0, 'Eta Psc', '#ffcc99'), // Eta
    ],
    lines: [[0, 3], [3, 2], [2, 1], [1, 0]]
  }
];


