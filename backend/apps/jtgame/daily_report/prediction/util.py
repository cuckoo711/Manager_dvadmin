import numpy as np
import tensorflow as tf
from keras.src.utils import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from multiprocessing import Pool
from apps.jtgame.daily_report.models import DayliData

# 让TensorFlow仅使用CPU
tf.config.set_visible_devices([], 'GPU')

# 设置 TensorFlow 使用的线程数，在导入 TensorFlow 后进行设置
def process_product_data(product_data):
    """
    归一化处理每个商品的数据
    为每个进程创建独立的Scaler实例
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    return scaler.fit_transform(product_data.reshape(-1, 1)).reshape(-1)

def parallel_data_preprocessing(all_products_data):
    """
    使用多进程处理所有商品的数据
    每个进程使用独立的Scaler实例
    """
    with Pool(processes=8) as pool:
        all_data_scaled = pool.map(process_product_data, all_products_data)
    return np.array(all_data_scaled)

def predict_income(all_products_data, e_product_data, window_size=3):
    e_product_data = np.array(e_product_data)

    # 使用pad_sequences进行填充
    all_data = pad_sequences(all_products_data, padding='post', dtype='float32')

    # 数据归一化：使用所有商品数据的归一化范围
    all_data_scaled = parallel_data_preprocessing(all_data)

    # 对每个商品数据做滑动窗口处理，生成输入特征
    def create_dataset(data, _window_size):
        X, y = [], []
        for i in range(len(data) - _window_size):
            X.append(data[i:i + _window_size])
            y.append(data[i + _window_size])
        return np.array(X), np.array(y)

    # 生成所有商品的输入特征和标签
    x_all, y_all = [], []
    for product_data_scaled in all_data_scaled:
        x, y = create_dataset(product_data_scaled, window_size)
        x_all.append(x)
        y_all.append(y)

    # 将每个商品的数据合并为一个大数据集
    x_all = np.concatenate(x_all, axis=0)
    y_all = np.concatenate(y_all, axis=0)

    # 将输入数据重塑为LSTM需要的形状
    x_all = x_all.reshape(x_all.shape[0], x_all.shape[1], 1)

    # 构建LSTM模型
    model = Sequential()

    # # 第一层LSTM层，增加Dropout和BatchNormalization
    # model.add(LSTM(units=200, return_sequences=True, input_shape=(x_all.shape[1], 1)))
    # model.add(Dropout(0.8))
    # model.add(BatchNormalization())
    #
    # # 第二层LSTM层，返回序列的设置
    # model.add(LSTM(units=50, return_sequences=False))
    # model.add(Dropout(0.2))
    # model.add(BatchNormalization())

    # 输出层
    model.add(Dense(1))

    # 使用Adam优化器，调整学习率
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss='mean_squared_error')

    # 早停和学习率调度器
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-6)

    # 训练模型
    model.fit(x_all, y_all, epochs=5, batch_size=64, validation_split=0.1, callbacks=[early_stopping, reduce_lr])

    # 对E商品的收入数据进行归一化
    scaler = MinMaxScaler(feature_range=(0, 1))
    e_data_scaled = scaler.fit_transform(e_product_data.reshape(-1, 1)).reshape(-1)

    # 使用滑动窗口处理E商品数据
    X_e, _ = create_dataset(e_data_scaled, window_size)

    # 重塑E商品数据为LSTM需要的输入形状
    X_e = X_e.reshape(X_e.shape[0], X_e.shape[1], 1)

    # 预测E商品第n+1天的收入
    predicted_income = model.predict(X_e[-1].reshape(1, window_size, 1))

    # 对预测结果进行反归一化
    predicted_income = scaler.inverse_transform(predicted_income.reshape(-1, 1))

    return predicted_income[0][0]


def test():
    import time
    st = time.time()
    banhaos = DayliData.objects.filter(banhao='天天有喜2', data_type=0).order_by('date')
    print('查询banhao耗时：', time.time() - st)
    all_products_data = []
    e_product_data = []
    st1 = time.time()
    all_game_names = list(banhaos.values_list('game_name', flat=True).distinct())[-15:]
    print('所有游戏名称：', all_game_names)
    print('查询游戏名称耗时：', time.time() - st1)
    st2 = time.time()
    for game_name in all_game_names:
        game_data = banhaos.filter(
            game_name=game_name, online_days__gt=0
        ).values_list('recharge', flat=True)
        if game_name == '天天有喜2（0.1折GM福利特权）':
            e_product_data = list(game_data)
        else:
            all_products_data.append(list(game_data))
    if not e_product_data:
        game_data = banhaos.filter(
            game_name='天天有喜2（0.1折GM福利特权）', online_days__gt=0
        ).values_list('recharge', flat=True)
        e_product_data = list(game_data)
    print('E商品的历史收入数据：', e_product_data)
    print('查询历史收入数据耗时：', time.time() - st2)
    st3 = time.time()
    predicted_income = predict_income(all_products_data, e_product_data)
    print(f'预测的天天有喜2（0.1折GM福利特权）第{len(e_product_data[:-1]) + 1}天的收入为：{predicted_income}')
    print('预测耗时：', time.time() - st3)
    print('总耗时：', time.time() - st)
