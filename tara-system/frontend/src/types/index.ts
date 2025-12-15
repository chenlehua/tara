// Enums
export enum ProjectStatus {
  DRAFT = 0,
  IN_PROGRESS = 1,
  COMPLETED = 2,
  ARCHIVED = 3,
}

export enum DocumentParseStatus {
  PENDING = 0,
  PARSING = 1,
  COMPLETED = 2,
  FAILED = 3,
}

export enum AssetType {
  ECU = 'ecu',
  BUS = 'bus',
  SENSOR = 'sensor',
  ACTUATOR = 'actuator',
  GATEWAY = 'gateway',
  EXTERNAL_INTERFACE = 'external_interface',
  DATA = 'data',
  FUNCTION = 'function',
}

export enum ThreatType {
  SPOOFING = 'Spoofing',
  TAMPERING = 'Tampering',
  REPUDIATION = 'Repudiation',
  INFORMATION_DISCLOSURE = 'Information Disclosure',
  DENIAL_OF_SERVICE = 'Denial of Service',
  ELEVATION_OF_PRIVILEGE = 'Elevation of Privilege',
}

export enum RiskLevel {
  NEGLIGIBLE = 1,
  LOW = 2,
  MEDIUM = 3,
  HIGH = 4,
  CRITICAL = 5,
}

export enum ImpactLevel {
  NEGLIGIBLE = 'negligible',
  MINOR = 'minor',
  MODERATE = 'moderate',
  MAJOR = 'major',
  SEVERE = 'severe',
}

export enum Likelihood {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  VERY_HIGH = 'very_high',
}

// Interfaces
export interface SecurityAttributes {
  confidentiality: 'low' | 'medium' | 'high'
  integrity: 'low' | 'medium' | 'high'
  availability: 'low' | 'medium' | 'high'
  authenticity?: 'low' | 'medium' | 'high'
}

export interface Asset {
  id: number
  projectId: number
  name: string
  assetType: AssetType
  category?: string
  description?: string
  securityAttrs?: SecurityAttributes
  interfaces?: AssetInterface[]
  parentId?: number
  children?: Asset[]
  createdAt: string
  updatedAt: string
}

export interface AssetInterface {
  name: string
  type: string
  protocol?: string
  direction: 'in' | 'out' | 'bidirectional'
}

export interface DamageScenario {
  id: number
  assetId: number
  name: string
  description?: string
  safetyImpact: ImpactLevel
  financialImpact: ImpactLevel
  operationalImpact: ImpactLevel
  privacyImpact: ImpactLevel
  impactLevel: ImpactLevel
}

export interface ThreatRisk {
  id: number
  projectId: number
  assetId: number
  threatName: string
  threatType: ThreatType
  description?: string
  impactLevel: ImpactLevel
  likelihood: Likelihood
  riskValue: number
  riskLevel: RiskLevel
  treatment?: string
  cal?: number
  attackPaths?: AttackPath[]
  createdAt: string
  updatedAt: string
}

export interface AttackPath {
  id: number
  threatRiskId: number
  name: string
  description?: string
  steps: AttackStep[]
  expertise: number
  elapsedTime: number
  equipment: number
  knowledge: number
  windowOfOpportunity?: number
  attackPotential: number
  feasibilityRating: string
  controlMeasures?: ControlMeasure[]
}

export interface AttackStep {
  order: number
  description: string
  technique?: string
}

export interface ControlMeasure {
  id: number
  attackPathId: number
  name: string
  description?: string
  controlType: string
  effectiveness: 'low' | 'medium' | 'high'
  status?: string
}

export interface Report {
  id: number
  projectId: number
  name: string
  template: string
  status: number
  filePath?: string
  statistics?: ReportStatistics
  createdAt: string
  updatedAt: string
}

export interface ReportStatistics {
  totalAssets: number
  totalThreats: number
  totalAttackPaths: number
  totalControlMeasures: number
  riskDistribution: Record<string, number>
}
