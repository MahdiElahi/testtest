using Application.Contracts;
using Application.Contracts.Interfaces;
using Application.Contracts.Interfaces.File;
using Application.Contracts.Interfaces.Product;
using Application.Contracts.Interfaces.Slider;
using Application.Contracts.Interfaces.SMS;
using Application.Contracts.Interfaces.SocialNetwork;
using Application.Contracts.Interfaces.User;
using Application.Services;
using Application.Services.JwtService;
using Application.Services.Sliders;
using Application.Services.SMS;
using Domain.Contracts;
using Domain.Entities.Auth;
using Infrastructure.Data;
using Infrastructure.Repositories;
using MasterDev.Client.Pages;
using MasterDev.Components;
using MasterDev.Components.Account;
using MasterDev.Middlewares;
using Microsoft.AspNetCore.Components.Authorization;
using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using MudBlazor;
using MudBlazor.Services;
using StackExchange.Redis;
using System.Globalization;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents()
    .AddInteractiveWebAssemblyComponents();

builder.Services.AddCascadingAuthenticationState();
builder.Services.AddScoped<IdentityUserAccessor>();
builder.Services.AddScoped<IdentityRedirectManager>();
builder.Services.AddScoped<AuthenticationStateProvider, PersistingRevalidatingAuthenticationStateProvider>();

builder.Services.AddIdentity<ApplicationUser, ApplicationRole>(options =>
{
    // Set password requirements
    options.SignIn.RequireConfirmedAccount = true;
    options.Password.RequireDigit = true; // Remove the need for a digit
    options.Password.RequireLowercase = false; // Remove the need for a lowercase character
    options.Password.RequireUppercase = false; // Remove the need for an uppercase character
    options.Password.RequireNonAlphanumeric = false; // Remove the need for a non-alphanumeric character
    options.Password.RequiredLength = 6; // Set the minimum password length to 6 characters
})
    .AddEntityFrameworkStores<ApplicationDbContext>()
    .AddSignInManager()
    .AddRoles<ApplicationRole>()

    .AddDefaultTokenProviders();



var connectionString = builder.Configuration.GetConnectionString("DefaultConnection") ?? throw new InvalidOperationException("Connection string 'DefaultConnection' not found.");

builder.Services.AddDbContextFactory<ApplicationDbContext>(options => options.UseSqlServer(connectionString));

builder.Services.AddDatabaseDeveloperPageExceptionFilter();


builder.Services.ConfigureApplicationCookie(options =>
{
    options.ExpireTimeSpan = TimeSpan.FromMinutes(30); // Set to whatever duration you prefer

    options.Events.OnRedirectToLogin = context =>
    {
        var requestPath = context.Request.Path.Value?.ToLower();

        if (!string.IsNullOrEmpty(requestPath) && requestPath.Contains("/admin-pro"))
        {
            context.Response.Redirect("/admin-pro/account/sign-in");
        }
        else
        {
            context.Response.Redirect("/account/sign-in"); // Default for client panel
        }

        return Task.CompletedTask;
    };
    options.Events.OnRedirectToAccessDenied = context =>
    {
        var requestPath = context.Request.Path.Value?.ToLower();

        if (!string.IsNullOrEmpty(requestPath) && requestPath.Contains("/admin-pro"))
        {
            context.Response.Redirect("/admin-pro/403");
        }
        else
        {
            context.Response.Redirect("/403"); // Default for client panel
        }

        return Task.CompletedTask;
    };
});


builder.Services.AddSignalR(hubOptions =>
{
    hubOptions.MaximumReceiveMessageSize = 1024000; // Example size limit in bytes
});

builder.Services.AddSingleton<IEmailSender<ApplicationUser>, IdentityNoOpEmailSender>();
builder.Services.AddHttpContextAccessor();
builder.Services.AddServerSideBlazor().AddCircuitOptions(option => { option.DetailedErrors = true; });

#region Services & Repositories
//Client
builder.Services.AddScoped<IAuthAdminService, AuthAdminService>();

builder.Services.AddScoped<IFileService, FileService>();
builder.Services.AddScoped<ISMSService, SMSService>();
//builder.Services.AddScoped<IRedisService, RedisService>();
builder.Services.AddScoped<IJwtService, JwtService>();
builder.Services.AddScoped<IAuthService, AuthService>();


builder.Services.AddScoped<IProductGroupAdminService, ProductGroupAdminService>();
builder.Services.AddScoped<IProductGroupService, ProductGroupService>();

builder.Services.AddScoped<ISocialNetworkAdminService, SocialNetworkAdminService>();
builder.Services.AddScoped<ISocialNetworkService, SocialNetworkService>();
builder.Services.AddScoped<ISocialNetworkRepository, SocialNetworkRepository>();

builder.Services.AddScoped<ISocialNetworkTypeAdminService, SocialNetworkTypeAdminService>();
builder.Services.AddScoped<ISocialNetworkTypeService, SocialNetworkTypeService>();
builder.Services.AddScoped<ISocialNetworkTypeRepository, SocialNetworkTypeRepository>();


builder.Services.AddScoped<IContactTypeAdminService, ContactTypeAdminService>();
builder.Services.AddScoped<IContactTypeService, ContactTypeService>();
builder.Services.AddScoped<IContactTypeRepository, ContactTypeRepository>();

builder.Services.AddScoped<IContactUsAdminService, ContactUsAdminService>();
builder.Services.AddScoped<IContactUsService, ContactUsService>();
builder.Services.AddScoped<IContactUsRepository, ContactUsRepository>();

builder.Services.AddScoped<IColorRepository, ColorRepository>();
builder.Services.AddScoped<IColorService, ColorService>();
builder.Services.AddScoped<IColorAdminService, ColorAdminService>();

builder.Services.AddScoped<IFeatureRepository, FeatureRepository>();
builder.Services.AddScoped<IFeatureService, FeatureService>();
builder.Services.AddScoped<IFeatureAdminService, FeatureAdminService>();

builder.Services.AddScoped<ISubFeatureRepository, SubFeatureRepository>();
builder.Services.AddScoped<ISubFeatureService, SubFeatureService>();
builder.Services.AddScoped<ISubFeatureAdminService, SubFeatureAdminService>();

builder.Services.AddScoped<IProductRepository, ProductRepository>();
builder.Services.AddScoped<IProductService, ProductService>();
builder.Services.AddScoped<IProductAdminService, ProductAdminService>();


builder.Services.AddScoped<IAuthRepository, AuthRepository>();

builder.Services.AddScoped<ISliderRepository, SliderRepository>();
builder.Services.AddScoped<ISliderAdminService, SliderAdminService>();
builder.Services.AddScoped<ISliderService, SliderService>();

builder.Services.AddScoped<IProductGroupRepository, ProductGroupRepository>();


builder.Services.AddScoped<IAccountAdminService, AccountAdminService>();

builder.Services.AddScoped<IShippingCostRepository, ShippingCostRepository>();
builder.Services.AddScoped<IShippingCostService, ShippingCostService>();
builder.Services.AddScoped<IShippingCostAdminService, ShippingCostAdminService>();

builder.Services.AddScoped<ILocationRepository, LocationRepository>();
builder.Services.AddScoped<ILocationService, LocationService>();

builder.Services.AddScoped<IAboutUsRepository, AboutUsRepository>();
builder.Services.AddScoped<IAboutUsAdminService, AboutUsAdminService>();
builder.Services.AddScoped<IAboutUsService, AboutUsService>();


builder.Services.AddScoped<IPostalAddressRepository, POstalAddressRepository>();
builder.Services.AddScoped<IPostalAddressService, PostalAddressService>();
builder.Services.AddScoped<IPostalAddressAdminService, PostalAddressAdminService>();

builder.Services.AddScoped<IOrderRepository, OrderRepository>();

builder.Services.AddScoped<IOrderService, OrderService>();
builder.Services.AddScoped<IOrderAdminService, OrderAdminService>();


builder.Services.AddAuthentication();
builder.Services.AddAuthorization();

builder.Services.AddScoped<IDialogService, DialogService>();


builder.Services.AddMudServices(config =>
{
    config.SnackbarConfiguration.PositionClass = Defaults.Classes.Position.TopCenter;
    config.SnackbarConfiguration.PreventDuplicates = false;
    config.SnackbarConfiguration.NewestOnTop = false;
    config.SnackbarConfiguration.ShowCloseIcon = true;
    config.SnackbarConfiguration.VisibleStateDuration = 5000;
    config.SnackbarConfiguration.HideTransitionDuration = 500;
    config.SnackbarConfiguration.ShowTransitionDuration = 500;
    config.SnackbarConfiguration.SnackbarVariant = Variant.Filled;

});
// Configure Redis
//builder.Services.AddSingleton<IConnectionMultiplexer>(sp =>
//{
//    var configurationOptions = ConfigurationOptions.Parse("localhost:6379"); // Adjust the connection string as needed
//    return ConnectionMultiplexer.Connect(configurationOptions);
//});

MapsterConfig.ConfigureMappings();

builder.Services.AddScoped<HtmlRenderer>();


#endregion



var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseWebAssemblyDebugging();
    app.UseMigrationsEndPoint();
}
else
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStatusCodePages(context =>
{
    // Check if status code is 404 (Not Found)
    if (context.HttpContext.Response.StatusCode == 404)
    {
        var requestPath = context.HttpContext.Request.Path.Value?.ToLower();

        if (!string.IsNullOrEmpty(requestPath) && requestPath.Contains("/admin-pro"))
        {
            // Redirect to admin custom 404 page
            context.HttpContext.Response.Redirect("/admin-pro/404");
        }
        else
        {
            // Redirect to client custom 404 page
            context.HttpContext.Response.Redirect("/404");
        }
    }

    return Task.CompletedTask;
});
//app.UseMiddleware<AuthMiddleware>();

app.UseAuthentication();  // Ensure authentication middleware is added
app.UseAuthorization();
app.UseAntiforgery();
app.UseStaticFiles(new StaticFileOptions
{
    OnPrepareResponse = ctx =>
    {
        const int durationInSeconds = 60 * 60 * 24 * 31;
        ctx.Context.Response.Headers[Microsoft.Net.Http.Headers.HeaderNames.CacheControl] =
                        "public,max-age=" + durationInSeconds;
    }
});
app.UseStatusCodePagesWithRedirects("/status-code/{0}");

app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode()
    .AddInteractiveWebAssemblyRenderMode()
    .AddAdditionalAssemblies(typeof(Counter).Assembly);

app.MapAdditionalIdentityEndpoints();


app.Run();
