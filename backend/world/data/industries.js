// Comprehensive list of industries for business applications
export const industries = [
  {
      "name": "Aeroespacial",
      "code": "ASP",
      "complexityScore": 9
  },
  {
      "name": "Agricultura y Ganadería",
      "code": "AGR",
      "complexityScore": 5
  },
  {
      "name": "Agronegocios",
      "code": "AgN",
      "complexityScore": 6
  },
  {
      "name": "Alimentos y bebidas",
      "code": "FOO",
      "complexityScore": 5
  },
  {
      "name": "Artículos personales y de uso doméstico",
      "code": "RET",
      "complexityScore": 5
  },
  {
      "name": "Asesoría contable y fiscal",
      "code": "ACC",
      "complexityScore": 7
  },
  {
      "name": "Automotriz",
      "code": "CAR",
      "complexityScore": 6
  },
  {
      "name": "Bancaria",
      "code": "BKG",
      "complexityScore": 9
  },
  {
      "name": "Bienes inmuebles",
      "code": "REA",
      "complexityScore": 6
  },
  {
      "name": "Bienes y servicios industriales",
      "code": "MAN",
      "complexityScore": 7
  },
  {
      "name": "Comercial",
      "code": "COM",
      "complexityScore": 6
  },
  {
      "name": "Comunicaciones/Publicaciones/Medios",
      "code": "MAP",
      "complexityScore": 6
  },
  {
      "name": "Consultoría/servicios empresariales",
      "code": "BSE",
      "complexityScore": 7
  },
  {
      "name": "Defensa/Fuerzas Armadas",
      "code": "DEF",
      "complexityScore": 9
  },
  {
      "name": "Educación/Academia",
      "code": "EDU",
      "complexityScore": 6
  },
  {
      "name": "Energía",
      "code": "ENU",
      "complexityScore": 8
  },
  {
      "name": "Gestión de fondos/activos",
      "code": "FAM",
      "complexityScore": 7
  },
  {
      "name": "Gobierno/Servicio Público",
      "code": "GPS",
      "complexityScore": 7
  },
  {
      "name": "Ingeniería/Construcción",
      "code": "ENC",
      "complexityScore": 7
  },
  {
      "name": "Jurídico",
      "code": "JUR",
      "complexityScore": 8
  },
  {
      "name": "Manufactura",
      "code": "MFG",
      "complexityScore": 7
  },
  {
      "name": "No gubernamental/sector terciario",
      "code": "NGO",
      "complexityScore": 6
  },
  {
      "name": "Productos de Consumo Masivo",
      "code": "CPG",
      "complexityScore": 6
  },
  {
      "name": "Productos químicos",
      "code": "PHC",
      "complexityScore": 7
  },
  {
      "name": "Público",
      "code": "pub",
      "complexityScore": 7
  },
  {
      "name": "Recursos primarios/minería",
      "code": "RES",
      "complexityScore": 7
  },
  {
      "name": "Retail/venta al por menor",
      "code": "RTL",
      "complexityScore": 6
  },
  {
      "name": "Salud y productos farmacéuticos",
      "code": "HEA",
      "complexityScore": 9
  },
  {
      "name": "Seguros",
      "code": "INS",
      "complexityScore": 8
  },
  {
      "name": "Servicios Financieros",
      "code": "FSE",
      "complexityScore": 9
  },
  {
      "name": "Servicios Funerarios",
      "code": "DTH",
      "complexityScore": 4
  },
  {
      "name": "Servicios Legales",
      "code": "LAW",
      "complexityScore": 8
  },
  {
      "name": "Tecnología de la información/Cómputo",
      "code": "ITC",
      "complexityScore": 9
  },
  {
      "name": "Telecomunicaciones",
      "code": "TEL",
      "complexityScore": 8
  },
  {
      "name": "Transporte/Logística",
      "code": "TRL",
      "complexityScore": 7
  },
  {
      "name": "Veterinaria",
      "code": "VET",
      "complexityScore": 5
  },
  {
      "name": "Viajes y ocio",
      "code": "TRV",
      "complexityScore": 6
  }
];

// Helper functions for industry data access
export const getIndustryByCode = (code) => {
  return industries.find(industry => industry.code === code);
};

export const getIndustryByName = (name) => {
  return industries.find(industry => industry.name === name);
};

export const getIndustriesSortedByName = () => {
  return [...industries].sort((a, b) => a.name.localeCompare(b.name));
};

export const getIndustryCodes = () => {
  return industries.map(industry => industry.code);
};

export const getIndustryNames = () => {
  return industries.map(industry => industry.name);
};

export const getIndustryComplexityScore = (industryName) => {
  const industry = industries.find(industry => industry.name === industryName);
  return industry?.complexityScore || 5; // Default to 5 if not found
};
