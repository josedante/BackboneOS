#!/bin/bash

echo "🔧 BackboneOS Dashboard Build Test"
echo "=================================="

# Limpiar cache y node_modules
echo "📦 Limpiando dependencias..."
rm -rf node_modules package-lock.json .nuxt .output

# Instalar dependencias
echo "📥 Instalando dependencias..."
npm install

# Build del proyecto
echo "🏗️ Compilando proyecto..."
npm run build

# Verificar que el build fue exitoso
if [ $? -eq 0 ]; then
    echo "✅ Build completado exitosamente!"
    echo ""
    echo "🚀 Para iniciar el servidor de desarrollo:"
    echo "   npm run dev"
    echo ""
    echo "🌐 Para preview de producción:"
    echo "   npm run preview"
else
    echo "❌ Build falló. Revisar errores arriba."
    exit 1
fi
