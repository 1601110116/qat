import torch

OPSET = 11
AXIS_OPSET = 11

# The following functions are from:
# https://github.com/Xilinx/brevitas


class QLinearConvFn(torch.autograd.Function):
    @staticmethod
    def symbolic(
            g, int_x,
            input_scale,
            input_zero_point,
            int_weight,
            weight_scale,
            weight_zero_point,
            output_scale,
            ouput_zero_point,
            output_dtype,
            int_bias,
            out_shape,
            kernel_size,
            padding,
            stride,
            groups,
            dilation):
        if int_bias is not None:
            ret = g.op(
                'QLinearConv', int_x,
                input_scale,
                input_zero_point,
                int_weight,
                weight_scale,
                weight_zero_point,
                output_scale,
                ouput_zero_point,
                int_bias,
                kernel_shape_i=kernel_size,
                pads_i=padding,
                strides_i=stride,
                group_i=groups,
                dilations_i=dilation)
        else:
            ret = g.op(
                'QLinearConv', int_x,
                input_scale,
                input_zero_point,
                int_weight,
                weight_scale,
                weight_zero_point,
                output_scale,
                ouput_zero_point,
                kernel_shape_i=kernel_size,
                pads_i=padding,
                strides_i=stride,
                group_i=groups,
                dilations_i=dilation)
        return ret

    @staticmethod
    def forward(
            ctx, int_x,
            input_scale,
            input_zero_point,
            int_weight,
            weight_scale,
            weight_zero_point,
            output_scale,
            output_zero_point,
            output_dtype,
            int_bias,
            out_shape,
            kernel_size,
            padding,
            stride,
            groups,
            dilation):
        return torch.empty(out_shape, dtype=output_dtype, device=int_x.device)


class DequantizeLinearFn(torch.autograd.Function):

    @staticmethod
    def symbolic(
            g, x,
            input_scale,
            input_zero_point,
            input_axis):
        if input_axis is not None and OPSET >= AXIS_OPSET:
            ret = g.op(
                'DequantizeLinear', x,
                input_scale,
                input_zero_point,
                axis_i=input_axis)
        else:
            ret = g.op(
                'DequantizeLinear', x,
                input_scale,
                input_zero_point)
        return ret

    @staticmethod
    def forward(
            ctx, int_x,
            input_scale,
            input_zero_point,
            input_axis):
        return int_x.float()


class QuantizeLinearFn(torch.autograd.Function):

    @staticmethod
    def symbolic(
            g, x,
            output_scale,
            ouput_zero_point,
            output_dtype,
            output_axis):
        if output_axis is not None and OPSET >= AXIS_OPSET:
            ret = g.op(
                'QuantizeLinear', x,
                output_scale,
                ouput_zero_point,
                axis_i=output_axis)
        else:
            ret = g.op(
                'QuantizeLinear', x,
                output_scale,
                ouput_zero_point)
        return ret

    @staticmethod
    def forward(
            ctx, x,
            output_scale,
            ouput_zero_point,
            output_dtype,
            output_axis):
        return x.type(output_dtype)

# The following functions are written by Xiaohu.


class QLinearLeakyReluFn(torch.autograd.Function):
    @staticmethod
    def symbolic(
            g, int_x,
            input_scale,
            input_zero_point,
            output_scale,
            ouput_zero_point,
            output_dtype,
            alpha):
        return g.op(
            'com.microsoft::QLinearLeakyRelu', int_x,
            input_scale,
            input_zero_point,
            output_scale,
            ouput_zero_point,
            alpha_f=alpha
        )

    @staticmethod
    def forward(
            ctx, int_x,
            input_scale,
            input_zero_point,
            output_scale,
            ouput_zero_point,
            output_dtype,
            alpha):
        return torch.empty_like(int_x).to(output_dtype)