from typing import Any

from app.resources.config import GENERAL_ERROR_MESSAGE


swagger_template: dict[str, Any] = {
	"swagger": "2.0",
	"info": {
		"title": "Tip Trip",
		"version": "1.0.0"
	},
	# "servers": [
	# 	{ "url": "http://localhost:5000" },
	# 	{ "url": "http://example.com:5000" }
	# ],
	"tags": [
		{ "name": "General", "description": "Endpoints for general purposes" },
		{ "name": "Places", "description": "Places CRUD operations" },
		{ "name": "Users", "description": "Users CRUD operations" },
		{ "name": "Models", "description": "Artificial intelligence models operations" }
	],
	"paths": {
		'/': {
			"get": {
				"tags": ["General"],
				"summary": "Shows a welcome message",
				"description": "Shows a welcome message.",
				"responses": {
					"200": {
						"description": "Shows a welcome message",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "Welcome to Tip Trip. Hope this tool helps you to improve your travel experiences" }
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				}
			},
		},
		"/apidocs": {
			"get": {
				"tags": ["General"],
				"summary": "Shows this API UI documentation",
				"description": "Shows this API UI documentation.",
				"responses": {
					"200": {
						"description": "Shows this API UI documentation",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": { "status": { "type": "string", "example": "Success" } }
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				}
			},
		},
		"/download/{os}": {
			"get": {
				"tags": ["General"],
				"summary": "Downloads app's Android or IOS instalation files",
				"description": "Downloads an app's Android or IOS instalation files based on the given information.",
				"parameters": [
					{
						"name": "os",
						"required": True,
						"in": "path",
						"schema": { "type": "string", "example": "android" },
						"description": "Host Operative Sistem, value can be either 'android' or 'ios'"
					},
				],
				"responses": {
					"200": {
						"description": "File downloaded successfully",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "File downloaded successfully" },
										"file": { "type": "string", "example": "..." },
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				}
			},
		},
		"/places": {
			"get": {
				"tags": ["Places"],
				"summary": "Retrieves all places",
				"description": (
					"Retrieves all places based on filters like classification, municipality, or current user's position coordinates.\n\n"
					"- If classification is provided, only places with that classification are retrieved.\n"
					"- If municipality is provided, only places from that municipality are retrieved.\n"
					"- If current user's position coordinates and distance are provided, places are retrieved based on the closest ones to the user's position.\n\n"
					"- If no filters are provided, all places are retrieved.\n\n"
					"Classification value can be one of: \n\n"
					"Álvaro Obregón, Azcapotzalco, Benito Juárez, Coyoacán, Cuajimalpa de Morelos, Cuauhtémoc, Gustavo A. Madero, Iztacalco, Iztapalapa, La Magdalena Contreras, Miguel Hidalgo, Milpa Alta, San Ángel, Tláhuac, Tlalpan, Venustiano Carranza, Xochimilco\n\n"
					"Municipality value can be one of: \n\n"
					"Arquitectura, Centro cultural, Centro religioso, Escultura, Experiencia, Monumento, Mural, Museo, Zona arqueológica"
				),
				"parameters": [
					{
						"name": "classification",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Arquitectura" }
					},
					{
						"name": "municipality",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Álvaro Obregón" }
					},
					{
						"name": "distance",
						"required": False,
						"in": "body",
						"schema": { "type": "integer", "format": "int64", "example": 5 }
					},
					{
						"name": "current_latitude",
						"required": False,
						"in": "body",
						"schema": { "type": "integer", "format": "float", "example": 19.4326 }
					},
					{
						"name": "current_longitude",
						"required": False,
						"in": "body",
						"schema": { "type": "integer", "format": "float", "example": -99.1332 }
					}
				],
				"responses": {
					"200": {
						"description": "Places retrieved successfully",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "Places retrieved successfully" },
										"places": {
											"type": "array",
											"items": { "$ref": "#/components/schemas/Place" }
										}
									}
								}
							}
						}
					},
					"204": {
						"description": "Successfully but no data found",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "No data found" }
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				},
				"security": [{ "bearerAuth": [] }]
			},
			"post": {
				"tags": ["Places"],
				"summary": "Creates a new place",
				"description": "Creates a new place with the provided information.",
				"parameters": [
					{
						"name": "name",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "Acroyoga, Pan y Circo" }
					},
					{
						"name": "classification",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "Centro cultural" }
					},
					{
						"name": "punctuation",
						"required": False,
						"in": "body",
						"schema": { "type": "integer", "format": "float", "example": 5.0 }
					},
					{
						"name": "description",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "A place to practice yoga" }
					},
					{
						"name": "schedules",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "9:00 - 18:00" }
					},
					{
						"name": "services",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Restrooms, Parking" }
					},
					{
						"name": "activities",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Yoga, Acrobatics" }
					},
					{
						"name": "prices",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Free" }
					},
					{
						"name": "permanent_exhibitions",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Statues" }
					},
					{
						"name": "temporal_exhibitions",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Art Gallery" }
					},
					{
						"name": "mail",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "example@example.com" }
					},
					{
						"name": "phone",
						"required": False,
						"in": "body",
						"schema": { "type": "integer", "format": "int64", "example": "5555555555" }
					},
					{
						"name": "website",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "http://example.com" }
					},
					{
						"name": "sic_website",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "http://sic.gob.mx/example" }
					},
					{
						"name": "cp",
						"required": True,
						"in": "body",
						"schema": { "type": "integer", "format": "int64", "example": 10001 }
					},
					{
						"name": "street_number",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "123 street A" }
					},
					{
						"name": "colony",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "Downtown" }
					},
					{
						"name": "municipality",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "Cuauhtémoc" }
					},
					{
						"name": "state",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "Ciudad de México" }
					},
					{
						"name": "latitude",
						"required": True,
						"in": "body",
						"schema": { "type": "number", "format": "float", "example": 40.785091 }
					},
					{
						"name": "longitude",
						"required": True,
						"in": "body",
						"schema": { "type": "number", "format": "float", "example": -99.968285 }
					},
					{
						"name": "how_to_arrive",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Near the main gate" }
					},
					{
						"name": "review",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Great place for a walk" }
					},
					{
						"name": "historic_review",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Visited by famous figures" }
					}
				],
				"responses": {
					"201": {
						"description": "Place created successfully",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "Place created successfully" },
										"id": { "type": "integer", "format": "int64", "example": 1 }
									}
								}
							}
						}
					},
					"409": {
						"description": "Place already exists",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": "Place already exists" }
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				},
				"security": [{ "bearerAuth": [] }]
			},
		},
		"/places/{id}" : {
			"get": {
				"tags": ["Places"],
				"summary": "Retrieves a place by its ID",
				"description": "Retrieves only one place by its ID.",
				"parameters": [
					{
						"name": "id",
						"required": True,
						"in": "path",
						"schema": { "type": "integer", "format": "int64", "example": 1 }
					},
				],
				"responses": {
					"200": {
						"description": "Place retrieved successfully",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "Place retrieved successfully" },
										"place": { "$ref": "#/components/schemas/Place" }
									}
								}
							}
						}
					},
					"404": {
						"description": "Place not found",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": "Place not found" }
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				},
				"security": [{ "bearerAuth": [] }]
			},
			"put": {
				"tags": ["Places"],
				"summary": "Updates a place by its ID",
				"description": "Updates a place by its ID and provided information.",
				"parameters": [
					{
						"name": "id",
						"required": True,
						"in": "path",
						"schema": { "type": "integer", "format": "int64", "example": 1 }
					},
					{
						"name": "name",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Acroyoga, Pan y Circo" }
					},
					{
						"name": "classification",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Centro cultural" }
					},
					{
						"name": "punctuation",
						"required": False,
						"in": "body",
						"schema": { "type": "integer", "format": "float", "example": 5.0 }
					},
					{
						"name": "description",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "A place to practice yoga" }
					},
					{
						"name": "schedules",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "9:00 - 18:00" }
					},
					{
						"name": "services",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Restrooms, Parking" }
					},
					{
						"name": "activities",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Yoga, Acrobatics" }
					},
					{
						"name": "prices",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Free" }
					},
					{
						"name": "permanent_exhibitions",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Statues" }
					},
					{
						"name": "temporal_exhibitions",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Art Gallery" }
					},
					{
						"name": "mail",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "example@example.com" }
					},
					{
						"name": "phone",
						"required": False,
						"in": "body",
						"schema": { "type": "integer", "format": "int64", "example": "5555555555" }
					},
					{
						"name": "website",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "http://example.com" }
					},
					{
						"name": "sic_website",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "http://sic.gob.mx/example" }
					},
					{
						"name": "cp",
						"required": False,
						"in": "body",
						"schema": { "type": "integer", "format": "int64", "example": 10001 }
					},
					{
						"name": "street_number",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "123 street A" }
					},
					{
						"name": "colony",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Downtown" }
					},
					{
						"name": "municipality",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Cuauhtémoc" }
					},
					{
						"name": "state",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Ciudad de México" }
					},
					{
						"name": "latitude",
						"required": False,
						"in": "body",
						"schema": { "type": "number", "format": "float", "example": 40.785091 }
					},
					{
						"name": "longitude",
						"required": False,
						"in": "body",
						"schema": { "type": "number", "format": "float", "example": -99.968285 }
					},
					{
						"name": "how_to_arrive",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Near the main gate" }
					},
					{
						"name": "review",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Great place for a walk" }
					},
					{
						"name": "historic_review",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Visited by famous figures" }
					}
				],
				"responses": {
					"201": {
						"description": "Place updated successfully",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "Place updated successfully" },
										"id": { "type": "integer", "format": "int64", "example": 1 }
									}
								}
							}
						}
					},
					"404": {
						"description": "Place not found",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": "Place not found" }
									}
								}
							}
						}
					},
					"409": {
						"description": "Place's name already exists",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": "Place's name already exists" }
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				},
				"security": [{ "bearerAuth": [] }]
			},
			"delete": {
				"tags": ["Places"],
				"summary": "Deletes a place by its ID",
				"description": "Deletes a place by its ID.",
				"parameters": [
					{
						"name": "id",
						"required": True,
						"in": "path",
						"schema": { "type": "integer", "format": "int64", "example": 1 }
					}
				],
				"responses": {
					"200": {
						"description": "Place deleted successfully",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "Place deleted successfully" },
										"id": { "type": "integer", "format": "int64", "example": 1 }
									}
								}
							}
						}
					},
					"404": {
						"description": "Place not found",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": "Place not found" }
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				},
				"security": [{ "bearerAuth": [] }]
			}
		},
		"/users": {
			"get": {
				"tags": ["Users"],
				"summary": "Retrieves all users",
				"description": "Retrieves all users.",
				"responses": {
					"200": {
						"description": "Users retrieved successfully",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "Users retrieved successfully" },
										"users": {
											"type": "array",
											"items": { "$ref": "#/components/schemas/User" }
										}
									}
								}
							}
						}
					},
					"204": {
						"description": "Successfully but no data found",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "No data found" }
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				},
				"security": [{ "bearerAuth": [] }]
			},
			"post": {
				"tags": ["Users"],
				"summary": "Creates a new user",
				"description": "Creates a new user with the provided information.",
				"parameters": [
					{
						"name": "username",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "Juan Perez" }
					},
					{
						"name": "mail",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "example@example.com" }
					},
					{
						"name": "password",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "mypassword" }
					}
				],
				"responses": {
					"201": {
						"description": "User created successfully",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "User created successfully" },
										"id": { "type": "integer", "format": "int64", "example": 1 }
									}
								}
							}
						}
					},
					"409": {
						"description": "User already exists",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": "User already exists" }
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				}
			}
		},
		"/users/auth": {
			"post": {
				"tags": ["Users"],
				"summary": "Authenticates a user",
				"description": "Authenticates a user with the provided information.",
				"parameters": [
					{
						"name": "mail",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "example@example.com" }
					},
					{
						"name": "password",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "mypassword" }
					},
				],
				"responses": {
					"201": {
						"description": "User authenticated successfully",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "User authenticated successfully" },
										"id": { "type": "integer", "format": "int64", "example": 1 },
										"token": { "type": "string", "example": "eyJhbGciOi ... kasjdhkHFGJHF " },
										"username": { "type": "string", "example": "Juan Perez" },
										"created_at": { "type": "string", "format": "date-time", "example": "2024-01-01T10:00:00Z" }
									}
								}
							}
						}
					},
					"401": {
						"description": "Invalid password",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": "Invalid password" }
									}
								}
							}
						}
					},
					"404": {
						"description": "User not found",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": "User not found" }
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				}
			}
		},
		"/users/{id}": {
			"get": {
				"tags": ["Users"],
				"summary": "Retrieves a user by its ID",
				"description": "Retrieves only one user by its ID.",
				"parameters": [
					{
						"name": "id",
						"required": True,
						"in": "path",
						"schema": { "type": "integer", "format": "int64", "example": 1 }
					},
				],
				"responses": {
					"200": {
						"description": "User retrieved successfully",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "User retrieved successfully" },
										"user": { "$ref": "#/components/schemas/User" }
									}
								}
							}
						}
					},
					"404": {
						"description": "User not found",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": "User not found" }
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				},
				"security": [{ "bearerAuth": [] }]
			},
			"put": {
				"tags": ["Users"],
				"summary": "Updates a user by its ID",
				"description": "Updates a user by its ID and provided information.",
				"parameters": [
					{
						"name": "id",
						"required": True,
						"in": "path",
						"schema": { "type": "integer", "format": "int64", "example": 1 }
					},
					{
						"name": "username",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "Juan Perez" }
					},
					{
						"name": "mail",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "example@example.com" }
					},
					{
						"name": "password",
						"required": False,
						"in": "body",
						"schema": { "type": "string", "example": "mypassword" }
					}
				],
				"responses": {
					"201": {
						"description": "User updated successfully",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "User updated successfully" },
										"id": { "type": "integer", "format": "int64", "example": 1 }
									}
								}
							}
						}
					},
					"404": {
						"description": "User not found",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": "User not found" }
									}
								}
							}
						}
					},
					"409": {
						"description": "User's mail already exists",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": "User's mail already exists" }
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				},
				"security": [{ "bearerAuth": [] }]
			},
			"delete": {
				"tags": ["Users"],
				"summary": "Deletes a user by its ID",
				"description": "Deletes a user by its ID.",
				"parameters": [
					{
						"name": "id",
						"required": True,
						"in": "path",
						"schema": { "type": "integer", "format": "int64", "example": 1 }
					}
				],
				"responses": {
					"200": {
						"description": "User deleted successfully",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "User deleted successfully" },
										"id": { "type": "integer", "format": "int64", "example": 1 }
									}
								}
							}
						}
					},
					"404": {
						"description": "User not found",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": "User not found" }
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				},
				"security": [{ "bearerAuth": [] }]
			}
		},
		"models/asr": {
			"post": {
				"tags": ["Models"],
				"summary": "Generates a text from an audio",
				"description": "Generates a text from a given audio data using a speech recognition artificial intelligence model",
				"parameters": [
					{
						"name": "audio",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "UklGRiQYAwBXQVZFZm10IB ... AAAAAAAAA//8=" },
						"description": "Audio data encoded in base64 format"
					}
				],
				"responses": {
					"201": {
						"description": "Speech recognition process completed successfully",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "Speech recognition process completed successfully" },
										"text": { "type": "string", "example": "Example text resulting by speech recognition process" }
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				},
				"security": [{ "bearerAuth": [] }]
			}
		},
		"models/agent": {
			"post": {
				"tags": ["Models"],
				"summary": "Generates a text response by an AI agent",
				"description": "Generates an audio response from a given prompt using both artificial intelligence's LLM and TTS models.",
				"parameters": [
					{
						"name": "prompt",
						"required": True,
						"in": "body",
						"schema": { "type": "string", "example": "How many turistic places does the app has?" }
					}
				],
				"responses": {
					"201": {
						"description": "Agent response process completed successfully",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Success" },
										"message": { "type": "string", "example": "Agent response process completed successfully" },
										"audio_data" : {
											"type": "object",
											"properties": {
												"nchannels": { "type": "integer", "format": "int64", "example": 1 },
												"sampwidth": { "type": "integer", "format": "int64", "example": 16000 },
												"framerate": { "type": "integer", "format": "int64", "example": 4096 },
												"comp_type": { "type": "string", "example": "DEFAULT" },
												"comp_name": { "type": "string", "example": "DEFAULT" },
												"duration": { "type": "integer", "format": "int64", "example": 45000 },
												"audio": { "type": "string", "example": "/f/9//z/AAD9/////v8 ... AAAAAAAAAAA==" }
											}
										}
									}
								}
							}
						}
					},
					"500": {
						"description": "Internal Server Error",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {
										"status": { "type": "string", "example": "Failed" },
										"message": { "type": "string", "example": GENERAL_ERROR_MESSAGE },
										"error_code": { "type": "string", "example": "TT.500" }
									}
								}
							}
						}
					}
				},
				"security": [{ "bearerAuth": [] }]
			}
		}
	},
	"components": {
		"schemas": {
			"Place": {
				"type": "object",
				"properties": {
					"id": { "type": "integer", "format": "int64", "example": 1 },
					"info": {
						"type": "object",
						"properties": {
							"name": { "type": "string", "example": "Central Park" },
							"classification": { "type": "string", "example": "Park" },
							"punctuation": { "type": "number", "format": "float", "example": 4.5 },
							"description": { "type": "string", "example": "A large public park" },
							"schedules": { "type": "string", "example": "9:00 - 18:00" },
							"services": { "type": "string", "example": "Restrooms, Parking" },
							"activities": { "type": "string", "example": "Jogging, Picnics" },
							"prices": { "type": "string", "example": "Free" },
							"permanent_exhibitions": { "type": "string", "example": "Historical Statues" },
							"temporal_exhibitions": { "type": "string", "example": "Art Gallery" },
							"mail": { "type": "string", "example": "info@centralpark.com" },
							"phone": { "type": "string", "example": "555-1234" },
							"website": { "type": "string", "example": "http://centralpark.com" },
							"sic_website": { "type": "string", "example": "http://sic.gob.mx/centralpark" }
						}
					},
					"address": {
						"type": "object",
						"properties": {
							"street_number": { "type": "string", "example": "123" },
							"colony": { "type": "string", "example": "Downtown" },
							"municipality": { "type": "string", "example": "New York" },
							"state": { "type": "string", "example": "NY" },
							"cp": { "type": "string", "example": "10001" },
							"latitude": { "type": "number", "format": "float", "example": 40.785091 },
							"longitude": { "type": "number", "format": "float", "example": -73.968285 },
							"how_to_arrive": { "type": "string", "example": "Near the main gate" }
						}
					},
					"reviews": {
						"type": "object",
						"properties": {
							"general": { "type": "string", "example": "Great place for a walk" },
							"historic": { "type": "string", "example": "Visited by famous figures" }
						}
					},
					"created_at": { "type": "string", "format": "date-time", "example": "2024-01-01T10:00:00Z" },
					"distance": { "type": "number", "format": "float", "example": 1.5 }
				}
			},
			"User": {
				"type": "object",
				"properties": {
					"id": { "type": "integer", "format": "int64", "example": 1 },
					"username": { "type": "string", "example": "Juan Perez" },
					"mail": { "type": "string", "example": "example@example.com" },
					"created_at": { "type": "string", "format": "date-time", "example": "2024-01-01T10:00:00Z" }
				}
			}
		},
		"securitySchemes": {
			"bearerAuth": {
				"type": "http",
				"scheme": "bearer",
				"bearerFormat": "JWT"
			}
		}
	}
}
