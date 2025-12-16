/**
 * Tests for utility helper functions
 */
import { describe, it, expect } from 'vitest'

// Mock utility functions (these would be in src/utils/helpers.ts)
const formatDate = (date: Date | string): string => {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toISOString().split('T')[0]
}

const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

const getRiskLevelColor = (level: string): string => {
  const colors: Record<string, string> = {
    critical: '#ff0000',
    high: '#ff6600',
    medium: '#ffcc00',
    low: '#00cc00',
    negligible: '#999999',
  }
  return colors[level.toLowerCase()] || '#999999'
}

const calculateProgress = (completed: number, total: number): number => {
  if (total === 0) return 0
  return Math.round((completed / total) * 100)
}

describe('Helper Functions', () => {
  describe('formatDate', () => {
    it('should format date object', () => {
      const date = new Date('2024-01-15T10:30:00Z')
      expect(formatDate(date)).toBe('2024-01-15')
    })

    it('should format date string', () => {
      expect(formatDate('2024-01-15T10:30:00Z')).toBe('2024-01-15')
    })
  })

  describe('truncateText', () => {
    it('should not truncate short text', () => {
      const text = 'Short'
      expect(truncateText(text, 10)).toBe('Short')
    })

    it('should truncate long text', () => {
      const text = 'This is a very long text that should be truncated'
      expect(truncateText(text, 10)).toBe('This is a ...')
    })

    it('should handle exact length', () => {
      const text = 'Exact'
      expect(truncateText(text, 5)).toBe('Exact')
    })
  })

  describe('getRiskLevelColor', () => {
    it('should return correct color for critical', () => {
      expect(getRiskLevelColor('critical')).toBe('#ff0000')
    })

    it('should return correct color for high', () => {
      expect(getRiskLevelColor('high')).toBe('#ff6600')
    })

    it('should return correct color for medium', () => {
      expect(getRiskLevelColor('medium')).toBe('#ffcc00')
    })

    it('should return correct color for low', () => {
      expect(getRiskLevelColor('low')).toBe('#00cc00')
    })

    it('should handle case insensitivity', () => {
      expect(getRiskLevelColor('CRITICAL')).toBe('#ff0000')
      expect(getRiskLevelColor('High')).toBe('#ff6600')
    })

    it('should return default color for unknown level', () => {
      expect(getRiskLevelColor('unknown')).toBe('#999999')
    })
  })

  describe('calculateProgress', () => {
    it('should calculate correct percentage', () => {
      expect(calculateProgress(5, 10)).toBe(50)
      expect(calculateProgress(3, 12)).toBe(25)
    })

    it('should handle zero total', () => {
      expect(calculateProgress(5, 0)).toBe(0)
    })

    it('should handle complete progress', () => {
      expect(calculateProgress(10, 10)).toBe(100)
    })

    it('should round to integer', () => {
      expect(calculateProgress(1, 3)).toBe(33)
    })
  })
})
