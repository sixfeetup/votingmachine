(function($) { $(function() {
    $("label.desc:contains('Team')").css("display","none");

    $("input[name='team_hasuser'][value='true']").each(function(){
        $(this).closest('fieldset').addClass('disable');
        $(this).closest('fieldset').find('input').prop('disabled', true);
    });
}); })(jQuery);