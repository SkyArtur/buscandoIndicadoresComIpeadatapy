from typing import Literal
import ipeadatapy as ip
import numpy as np
from datetime import datetime


def buscar_taxas(taxa: Literal['selic', 'ipca', 'cdi'], acumulado_ano_corrente: bool = False):
    """
    Obtém valores das taxas Selic, IPCA ou CDI.
    Calcula o acumulado do ano corrente ou dos últimos 12 meses para IPCA e CDI.

    :param taxa: Literal['selic', 'ipca', 'cdi']
    :param acumulado_ano_corrente: bool - Se True, calcula o acumulado apenas do ano vigente.
    :return: float - Taxa ou acumulado calculado.
    """
    def check_dataframe(dataframe, selic_columns: bool = False):
        colunas_requeridas = ['YEAR', 'VALUE ((% a.m.))' if not selic_columns else 'VALUE ((% a.a.))']
        if not dataframe.empty and all(col in dataframe.columns for col in colunas_requeridas):
            return True
        raise ValueError('Estrutura inesperada no dataframe.')

    def prod(indexador, periodo):
        check_dataframe(indexador)
        ano_corrente = indexador[indexador['YEAR'] == ano]['VALUE ((% a.m.))']
        doze_meses = indexador['VALUE ((% a.m.))'][-12:]
        return np.prod([1 + (var / 100) for var in (ano_corrente if periodo else doze_meses)]) - 1

    try:
        ano = datetime.today().year
        hoje = datetime.today().strftime('%Y/%m/%d')
        match taxa:
            case 'selic':
                selic = ip.timeseries('BM366_TJOVER366', year=ano)
                check_dataframe(selic, True)
                return selic['VALUE ((% a.a.))'].iloc[-1] / 100
            case 'ipca':
                ipca = ip.timeseries('PRECOS12_IPCAG12', yearGreaterThan=ano - 2)
                return prod(ipca, acumulado_ano_corrente)
            case 'cdi':
                cdi = ip.timeseries('BM12_TJCDI12', yearGreaterThan=ano - 2)
                return prod(cdi, acumulado_ano_corrente)
            case _:
                raise ValueError(f'Taxa "{taxa}" invalida! Use "selic" or "ipca" or "cdi".')
    except (Exception, TypeError, ValueError, ZeroDivisionError) as error:
        return {'error': str(error)}


print(f"""
SELIC = {buscar_taxas('selic') * 100} %
IPCA acumulado em 12 = {buscar_taxas('ipca') * 100:.2f} %
IPCA 2024 = {buscar_taxas('ipca', True) * 100:.2f} %
CDI 2024 = {buscar_taxas('cdi', True) * 100:.2f} %
CDI acumulado em 12 = {buscar_taxas('cdi') * 100:.2f} %
""")
