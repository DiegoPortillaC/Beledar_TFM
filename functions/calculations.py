def calcular(precio_carnes: float, num_carnes: int, precio_venta: float):
    """
    Calcula beneficio y desglose para Beledar.

    Returns:
        dict: {
            beneficio, precio_total_carnes, gastos_pimientos, gastos_polvos,
            pimientos, polvos, posibles_beledar
        }
    """
    carnes_estimadas = num_carnes * 1.35
    posibles_beledar = ((carnes_estimadas / 15) * 1.05) * 3
    precio_total_carnes = precio_carnes * num_carnes
    pimientos = (carnes_estimadas / 15) * 5
    polvos = (carnes_estimadas / 15) * 40
    gastos_pimientos = pimientos * 0.098
    gastos_polvos = polvos * 0.0688
    beneficio = (precio_venta * posibles_beledar) - (gastos_pimientos + gastos_polvos + precio_total_carnes)
    return {
        "beneficio": beneficio,
        "precio_total_carnes": precio_total_carnes,
        "gastos_pimientos": gastos_pimientos,
        "gastos_polvos": gastos_polvos,
        "pimientos": pimientos,
        "polvos": polvos,
        "posibles_beledar": posibles_beledar
    }
