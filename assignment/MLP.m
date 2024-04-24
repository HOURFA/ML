% clear ;
close all;
load DigitsDataTrain.mat;
load DigitsDataTest.mat;

% Hyperparameters
batch_size = 100;
epoch = 10000;
learning_rate = 0.1;
Tolerance = 1e-4;

% model parameters
input_size = 784;
hidden_layer_num = 1;
hidden_size = 50*2^(hidden_layer_num-1);
output_size = 10; 
    
[params, grad, train_loss_list] = train(XTrain, labelsTrain, batch_size, learning_rate, epoch, input_size, hidden_size, output_size, hidden_layer_num, Tolerance);

draw_loss(train_loss_list, epoch);
predict(XTest, labelsTest, params, 100, hidden_layer_num);

function predict(input, label, params, batch_size, hidden_layer_num)

    fprintf('Prediction is start!\n')
    x = input(:,:,:);
    x = reshape(x, [size(x, 1)*size(x, 2), size(x, 3)])';
    data_num = size(x, 1);
    t = zeros(data_num,10);
    idx = double(label(:,:,:));
    for i = 1:data_num
        t(i,idx(i)) = 1;
    end
    batch_mask = randperm(data_num, batch_size);
    x_batch = x(batch_mask, :);
    t_batch = t(batch_mask, :);    
    tic;
    pred = myForward(params, x_batch, hidden_layer_num);
    process_time = toc;
    disp(['Prediction time : ', num2str(process_time),' (s)']);
    [~, act_idx] = max(t_batch, [], 2);
    [~,pred_idx] = max(pred.y, [], 2);
    correct = sum(act_idx == pred_idx)/batch_size *100;
    fprintf('act : %3.0f%%\n',correct);
    fprintf('Prediction is done!\n')
    show_data(x_batch, batch_size, act_idx-1, pred_idx-1)
end
function [params, grad, train_loss_list] = train(input, label, batch_size,learning_rate, epoch, input_size, hidden_size, output_size, hidden_layer_num, Tolerance)
    train_loss_list = struct();

    fprintf('Training is start!\n')
    x = input(:,:,:);
    x = reshape(x, [size(x, 1)*size(x, 2), size(x, 3)])';%flatten
    data_num = size(x, 1);
    t = zeros(data_num,output_size);
    idx = double(label(:,:,:));
    for i = 1:data_num  % Put the label index to the one-hot array(t)
        t(i,idx(i)) = 1;
    end
    params = init_network(input_size,hidden_size,output_size, hidden_layer_num);
    tic;
    h = waitbar(0, 'Traning...0%');
    for i = 1:epoch    
        clc
        batch_mask = randperm(data_num, batch_size);
        x_batch = x(batch_mask, :);
        t_batch = t(batch_mask, :);
        grad = myBackward(params, x_batch, t_batch, hidden_layer_num);
        params = gradient_descent(params, grad, learning_rate);        
        loss = loss_func(params, x_batch, t_batch, hidden_layer_num);
        if loss < Tolerance
            fprintf("Training loss did not improve more than tol=%d. Stopping.",Tolerance)
            break
        end
        % fprintf('epoch: %d, loss: %0.5f', i, loss);
        waitbar(i / epoch, h, sprintf('Traning...%d%% , loss...%0.5f', round(i / epoch * 100), loss));
        str = ['epoch_', num2str(i)];
        train_loss_list.(str) = loss;
    end
    close(h);
    process_time = toc;
    disp(['Training time : ', num2str(process_time),' (s)']);
    fprintf('Training is done!\n')
end
% % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % MODEL
function params = init_network(input_size, hidden_size, output_size, hidden_layer_num)
    weight_init_std = 0.01;
    
    params = struct();
    
    for i = 1:hidden_layer_num
        if i == 1
            hidden_input_size = input_size;
            hidden_output_size = hidden_size;
        else
            hidden_input_size = hidden_output_size;
            hidden_output_size = round(hidden_input_size/2);
        end
        params.(['W' num2str(i)]) = weight_init_std * randn(hidden_input_size, hidden_output_size);
        params.(['b' num2str(i)]) = zeros(1, hidden_output_size);        
    end
    params.(['W' num2str(hidden_layer_num + 1)]) = weight_init_std * randn(hidden_output_size, output_size);
    params.(['b' num2str(hidden_layer_num + 1)]) = zeros(1, output_size);
end

function pred = myForward(params, x, hidden_layer_num)
    pred = struct();
    for i = 1:hidden_layer_num
        if i == 1
            pred.a1 = x * params.W1  + params.b1;
            pred.z1 = sigmoid(pred.a1);
        else
            pred.(['a' num2str(i)]) = pred.(['z' num2str(i-1)]) * params.(['W' num2str(i)]) + params.(['b' num2str(i)]);
            pred.(['z' num2str(i)]) = sigmoid(pred.(['a' num2str(i)]));
        end        
    end
    pred.(['a' num2str(hidden_layer_num+1)]) = pred.(['z' num2str(hidden_layer_num)]) * params.(['W' num2str(hidden_layer_num + 1)]) + params.(['b' num2str(hidden_layer_num + 1)]);
    pred.y = softmax(pred.(['a' num2str(hidden_layer_num + 1)])); 
end
function grad = myBackward(params, x, t, hidden_layer_num)

    batch_num = size(x, 1);

    %forward
    back_pred = myForward(params, x, hidden_layer_num);

    %backward
    dy = (back_pred.y - t) / batch_num;

    grad.(['W' num2str(hidden_layer_num+1)]) = back_pred.(['z' num2str(hidden_layer_num)])' * dy;
    grad.(['b' num2str(hidden_layer_num+1)]) = sum(dy,1);
    for i = hidden_layer_num:-1:1
        if i == hidden_layer_num
            dz = dy * params.(['W' num2str(i+1)])';
        else
            dz = dz * params.(['W' num2str(i+1)])';
        end
        da = sigmoid_grad(back_pred.(['a' num2str(i)])) .* dz;
        if i == 1   
            grad.W1 = x' * da;
        else    
            grad.(['W' num2str(i)]) = back_pred.(['z' num2str(i-1)])' * da;
        end
        grad.(['b' num2str(i)]) = sum(da,1);
    end    
end
% % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % ACTIVATION　FUNCTIONS
function y = softmax(x)
    c = max(x,[],2);
    exp_x = exp(x-c);
    sum_exp_x = sum(exp_x, 2);
    y = exp_x ./ sum_exp_x;
end
function y = sigmoid(x)
    y = 1 ./ (1 + exp(-x));
end
function y = sigmoid_grad(x)
    y = (1 - sigmoid(x)) .* sigmoid(x);
end
% % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % LOSS　FUNCTIONS
function params = gradient_descent(params, grad, learning_rate)

    fields = fieldnames(params);
    for i = 1:numel(fields)
        field_name = fields(i);
        params.(field_name{1}) =  params.(field_name{1}) - learning_rate * grad.(field_name{1});
    end

end
function l = loss_func(params, x, t, hidden_layer_num)

    pred = myForward(params, x, hidden_layer_num);
    l = cross_entropy_error(pred.y, t);

end
function l = cross_entropy_error(y, t)  

    delta = 1e-7;
    batch_num = size(y, 1);
    l = 0;
    if sum(t,2) > 1        
        t = one_hot(t);
    end
    for i = 1:batch_num
        [~,t_idx] = max(t(i, :));
        loss = -log(y(i,t_idx) + delta)/batch_num;
        l = l + loss;
    end

end
function draw_loss(train_loss_list, epoch)

    fields = fieldnames(train_loss_list);   
    values = zeros(1, numel(fields));    
    for i = 1:numel(fields)
        field_name = fields{i};
        values(i) = train_loss_list.(field_name);       
    end 
    plot(values)
    ylim([0, 10])
    xlim([0, epoch])
    xlabel('Epoch');
    ylabel('Loss');

end
function onehot = one_hot(array)

    [~, max_index] = max(array, [], 2);    
    onehot = zeros(1, length(array));   
    onehot(max_index) = 1;
    
end
function show_data(array, num,act,pred)

    reshaped_samples = reshape(array', [28, 28, num]);
    n_cols = ceil(sqrt(num));
    n_rows = ceil(num / n_cols); 
    for i = 1:num
        subplot(n_cols, n_rows, i);
        imshow(reshaped_samples(:, :, i));                
        if act(i) ~= pred(i)
            title(['act : ', num2str(act(i)),' , pred : ',num2str(pred(i))],'Color','red')
        else
            title(['act : ', num2str(act(i)),' , pred : ',num2str(pred(i))]);
        end
    end
end

