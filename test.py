from gsheet_util import gsheet_write_row_by_dict as log_result


def test():
    log_result({
        'epsilon': 0.1,
        'lambda': 1,
        'hidden_layer_number': 4,
        'rmse': 0.2,
        'b': 4,
        'c': 2,
        'd': 5,
    })


if __name__ == '__main__':
    test()
