import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { loadStarCatalog } from './star-catalog'
import starCatalogData from '../../../public/data/star-catalog/star-catalog.json'

const originalFetch = globalThis.fetch

describe('loadStarCatalog', () => {
  const testStars = [
    {
      hip: 330,
      alpha: 1.5114914110744684,
      delta: 62.481523819408466,
      mag: 5.9,
      pmRA: -4.799655442984407e-9,
      pmDE: -1.7938106201052832e-9,
      bvColor: 0.274,
      distance: 3665.1685393258426,
    },
    {
      hip: 343,
      alpha: 1.5278277879113935,
      delta: -16.33561288587673,
      mag: 5.78,
      pmRA: 2.606843163325975e-7,
      pmDE: -2.9219720560471737e-7,
      bvColor: 1.084,
      distance: 288.9282550930027,
    },
    {
      hip: 355,
      alpha: 1.5708758914230223,
      delta: -10.315759178827223,
      mag: 4.99,
      pmRA: -3.146440790400889e-8,
      pmDE: -5.759586531581288e-8,
      bvColor: 1.619,
      distance: 1606.8965517241381,
    },
  ]

  beforeEach(() => {
    // Mock fetch to return actual star catalog data
    globalThis.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(starCatalogData),
      } as Response),
    )
  })

  afterEach(() => {
    // Restore original fetch
    globalThis.fetch = originalFetch
  })

  test('stars number is right', async () => {
    const result = await loadStarCatalog()

    // Verify the result length matches actual data
    expect(result.length).toBe(starCatalogData.length)
    // Verify fetch was called with correct path
    expect(globalThis.fetch).toHaveBeenCalledWith('/data/star-catalog/star-catalog.json')
  })

  test('correctly transforms raw star data fields to StarMeta format', async () => {
    // Mock fetch with test data
    globalThis.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(testStars),
      } as Response),
    )

    const result = await loadStarCatalog()

    // Verify each test star is correctly mapped
    testStars.forEach((testStar) => {
      const star = result.find((s) => s.hIP === testStar.hip)
      expect(star).toBeDefined()
      expect(star!.hIP).toBe(testStar.hip)
      expect(star!.equatorialCoordinate?.rightAscension).toBe(testStar.alpha)
      expect(star!.equatorialCoordinate?.declination).toBe(testStar.delta)
      expect(star!.magnitude).toBe(testStar.mag)
      expect(star!.pmRA).toBe(testStar.pmRA)
      expect(star!.pmDE).toBe(testStar.pmDE)
      expect(star!.bvColor).toBe(testStar.bvColor)
    })
  })
})
