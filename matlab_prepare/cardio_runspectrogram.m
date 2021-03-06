% ��������� �������� �� �������������� �������� (������� ������ CardioQVARK - �������� ���������, ��� ���)

m_train = csvread('data_fake_aps_train_spectrogram.csv')
length(m_train)
[rows, cols] = size(m_train)

F = [];
for i=1:rows
    x = m_train(i,2:cols);
    [s,f,t] = spectrogram(x,50,0);
    s2 = log(abs(s));
    F(:,i) = mean(abs(diff(s2'))); % mean(s2,2)
    disp(i)
end;
F = F';
y = m_train(:,1);
dlmwrite('data_fake_aps_train_spectrogram_out.csv', [y F(:,:)])

m_train = csvread('data_fake_aps_hold_spectrogram.csv')
length(m_train)
[rows, cols] = size(m_train)
F = [];
for i=1:rows
    x = m_train(i,2:cols);
    [s,f,t] = spectrogram(x,50,0);
    s2 = log(abs(s));
    F(:,i) = mean(abs(diff(s2'))); % mean(s2,2)
    disp(i)
end;
F = F';
y = m_train(:,1);
dlmwrite('data_fake_aps_hold_spectrogram_out.csv', [y F(:,:)])