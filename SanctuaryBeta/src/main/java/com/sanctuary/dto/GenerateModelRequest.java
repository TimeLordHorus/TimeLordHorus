package com.sanctuary.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class GenerateModelRequest {

    @NotBlank(message = "Prompt is required")
    @Size(max = 500, message = "Prompt must be less than 500 characters")
    private String prompt;

    private String quality = "medium"; // low, medium, high

    private String style = "realistic"; // realistic, stylized, abstract
}
