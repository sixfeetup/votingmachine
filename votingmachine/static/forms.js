(function($) { $(function() {
    $("label.desc:contains('Team')").css("display","none");

    $("input[name='team_hasuser'][value='true']").each(function(){
        fieldset = $(this).closest('fieldset')
        $(fieldset).addClass('disable');
        $(fieldset).find('input').prop('disabled', true);
        $(fieldset).prepend('<p class="novote">You cannot vote for your own group</p>');
    });
}); })(jQuery);