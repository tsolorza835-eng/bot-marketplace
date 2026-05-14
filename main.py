                # Filtrar por rango de precio
                if not (precio_minimo <= precio_num <= precio_maximo):
                    detalle.close()
                    continue

                # Filtrar por puntaje mínimo solicitado
                if puntaje < puntaje_minimo:
                    detalle.close()
                    continue

                # Agregar solo las publicaciones que cumplan los criterios
                oportunidades.append({
                    "titulo": titulo,
                    "precio": precio,
                    "puntaje": puntaje,
                    "categoria": categoria,
                    "url": url,
                })